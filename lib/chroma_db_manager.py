import os
import hashlib
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm
from typing import List, Dict, Optional
import PyPDF2
import docx
import csv

class ChromaDBManager:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="documents", 
            embedding_function=self.ef
        )
        # 存储文件哈希值避免重复
        self.file_hashes = set(self._load_hashes())

    def _file_hash(self, file_path: str) -> str:
        """计算文件MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _load_hashes(self) -> List[str]:
        """从元数据加载已有哈希值"""
        existing = self.collection.get(include=["metadatas"])
        return [m["hash"] for m in existing["metadatas"] if "hash" in m]

    def _load_file(self, file_path: str) -> str:
        """加载不同文件类型的内容"""
        ext = os.path.splitext(file_path)[1].lower()
        content = ""
        
        if ext == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content += page.extract_text() + "\n"
                    
        elif ext == ".docx":
            doc = docx.Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
        elif ext == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                content = "\n".join([",".join(row) for row in reader])
                
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
        return content

    def add_files(self, file_paths: List[str], batch_size: int = 100):
        """添加多个文件到数据库"""
        new_hashes = set()
        documents, metadatas, ids = [], [], []
        skipped = 0
        
        # 过滤已存在文件
        valid_files = []
        for path in file_paths:
            file_hash = self._file_hash(path)
            if file_hash in self.file_hashes:
                skipped += 1
                continue
            valid_files.append((path, file_hash))
            new_hashes.add(file_hash)
        
        # 处理有效文件
        for i, (path, file_hash) in tqdm(
            enumerate(valid_files), 
            total=len(valid_files),
            desc="Processing files"
        ):
            try:
                content = self._load_file(path)
                documents.append(content)
                metadatas.append({"source": path, "hash": file_hash})
                ids.append(f"doc_{len(self.file_hashes) + i + 1}")
                
                # 批量提交
                if (i + 1) % batch_size == 0:
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    documents, metadatas, ids = [], [], []
                    
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
        
        # 提交剩余文档
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        # 更新哈希集合
        self.file_hashes.update(new_hashes)
        print(f"Added {len(valid_files)} files, skipped {skipped} duplicates")

    def query(self, query_text: str, n_results: int = 1) -> List[Dict]:
        """查询相似文档"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist
            } 
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]

    def delete_by_source(self, file_path: str):
        """根据文件路径删除文档"""
        results = self.collection.get(where={"source": file_path})
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            # 从哈希集中移除
            for meta in results["metadatas"]:
                if "hash" in meta:
                    self.file_hashes.discard(meta["hash"])
            print(f"Deleted {len(results['ids'])} documents from {file_path}")
        else:
            print("No documents found for this path")
    '''
    def clear_all(self):
        """清空整个集合"""
        self.collection.delete(where={"$ne": None})
        self.file_hashes = set()
        print("All documents cleared")
    '''
    def clear_all(self):
        """清空整个集合"""
        try:
            # 删除集合
            self.client.delete_collection("documents")
            # 重新创建集合
            self.collection = self.client.get_or_create_collection(
                name="documents", 
                embedding_function=self.ef
            )
            self.file_hashes = set()  # 清空哈希集合
            print("All documents cleared")
        except Exception as e:
            print(f"Error clearing all documents: {e}")
    
