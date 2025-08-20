from lib.chroma_db_manager import ChromaDBManager
#from spark_api import SparkAPI
import os
from pathlib import Path
from typing import List, Dict, Callable, Optional, TYPE_CHECKING  
import os
os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'
os.environ['SSL_CERT_FILE'] = '/etc/ssl/certs/ca-certificates.crt'
# 初始化向量数据库
db_manager = ChromaDBManager()
file_paths = [str(path) for path in Path("documents").glob("*") if path.is_file()]
# 添加文件到数据库
#file_paths = ["doc1.pdf", "report.docx", "data.csv"]
db_manager.add_files(file_paths)
'''
# 删除指定文件
db_manager.delete_by_source("doc1.pdf")

# 清空数据库
# db_manager.clear_all()
'''
