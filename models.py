#参与本项目者必须模块化编程!
from lib.chroma_db_manager import ChromaDBManager
from pathlib import Path
from typing import List, Dict, Callable, Optional, TYPE_CHECKING  
import os
from lib.config import appid, api_key, api_secret, Spark_lite, domain_lite, Spark_deepthink, domain_dt, Spark_Ultra, domain_Ultra
from lib.chat_spark_api import Common_Chat_Api
import sqlite3


############Init_Environment#########

os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'
os.environ['SSL_CERT_FILE'] = '/etc/ssl/certs/ca-certificates.crt'
################################
'''
1.配置文件说明:
    .lib/config.py:
        Spark_lite
        domain_lite
        Spark_deepthink
        domain_dt
        Spark_Ultra
        domain_Ultra
2.其他文件的类的说明:
##########lib.chat_spark_api##########
    Common_Chat_Api(in lib.check_spark_api): 
        #Warning:后续加temperature
        .chat('prompt') :对话
        .clear_history():清除对话历史
        .check_history():检查调试对话历史
###############################
##########lib.chroma_db_manager######
    ChromaDBManager(persist_dir="dir"):
        .add_files(files_path) :添加文件到向量数据库
        .query(query_text):检索向量数据库
            return:
                return_text :str
                hash & source :dict
                distence :float
        .delete_by_source(file):删除文件
        .clear_all() :清空数据库(Danger!)
################################
'''
class Chat_All_Methods:
    def __init__(self, with_web_search=False, with_history=False ,with_chroma_db_search=False, AI_url=Spark_lite, domain_type=domain_lite):
        self.with_web_search = with_web_search;
        self.with_history = with_history;
        self.with_chroma_db_search = with_chroma_db_search;
        self.AI_url = AI_url;
        self.domain_type = domain_type;
        self.web_search_v1_prompt = ""
        self.cut_line_bottom = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        pass
    
    def Chat_base(self,base_question, with_history = False):
        #with_history, AI_url, domain_type 在self中直接调用
        chat_base = Common_Chat_Api(domain=self.domain_type, url=self.AI_url)
        if self.with_history:
            try:
                result = chat_base.chat(base_question)
                return result
            except Exceptions as err_all_with_history:
                err_all_with_history = "[ERROR]" + err_all_with_history
                return err_all_with_history
        else:
            try:
                result = chat_base.chat(base_question)
                chat_base.clear_history() #Warning:正式上线前，为了对大量用户，减小内存负担，需要改为存储进数据库
                return result
            except Exceptions as err_all_no_history:
                err_all_no_history = "[ERROR]" + err_all_no_history
                return err_all_no_history
        pass
    
    def Knowledge_base_query(self,prompt):
        search_pointer = ChromaDBManager()
        results = search_pointer.query(prompt)
        return_text = ""
        for result in results:
            return_text += "#########{file_source_name}########".format(file_source_name = result["metadata"]['source'])
            return_text += "\n" + result["content"] +"\n" + "###############################" + "\n"
            #print(result["distance"]) debug
        return return_text
     
    def Website_search_query_v1(self,prompt):
        temperature=0.8
        max_tokens=8192
        #利用星火大模型Ultra4.0,联网搜索
        Ultra_chat=Common_Chat_Api(domain=domain_Ultra, url=Spark_Ultra, temperature=temperature, max_tokens=max_tokens)
        Ultra_chat.clear_history()
        try:
            result=Ultra_chat.chat(prompt)
            return result
        except Exception as err_ultra:
            err_ultra = "[Error]" + err_ultra
            return err_ultra
        pass
    
    def is_history_change(self,with_history):
        self.with_history=with_history
        pass
    
    def cdb_web_search(self,prompt): #联网,知识库综合查询
        question = ""
        try:
            knowledge_result = self.Knowledge_base_query(prompt)
            web_search_v1_result = self.Website_search_query_v1(self.web_search_v1_prompt)
            question += self.cut_line("本地知识库查询结果") + "\n" + knowledge_result + "\n" + self.cut_line_bottom + "\n" +self.cut_line("联网查询结果") + "\n" + web_search_v1_result + "\n" + self.cut_line_bottom + "\n" + "综合上述知识库查询和联网查询获得的资料，知识库查询结果优先级高于联网查询结果，根据以上信息，回答下列问题:" + "\n" + prompt
            mix_result=self.Chat_base(question)
            return prompt,knowledge_result,web_search_v1_result,mix_result
        except Exception as err_mix:
            err_mix="[Error]" + str(err_mix)
            return prompt,knowledge_result,web_search_v1_result,err_mix
                
    def web_search(self,prompt): #联网查询
        knowledge_result=""
        question = ""
        try:
            web_search_v1_result = self.Website_search_query_v1(self.web_search_v1_prompt)
            question += self.cut_line("联网查询结果") + "\n" + web_search_v1_result + "\n" + self.cut_line_bottom + "\n" + "结合上述联网查询获得的资料，根据以上信息，回答下列问题:" + "\n" + prompt
            mix_result=self.Chat_base(question)
            return prompt,knowledge_result,web_search_v1_result,mix_result
        except Exception as err_mix:
            err_mix="[Error]" + str(err_mix)
            return prompt,knowledge_result,web_search_v1_result,err_mix
    def cdb_search(self,prompt): #知识库综合查询
        question = ""
        web_search_v1_result=""
        try:
            knowledge_result = self.Knowledge_base_query(prompt)
            question += self.cut_line("本地知识库查询结果") + "\n" + knowledge_result + "\n" + self.cut_line_bottom + "\n" + "结合上述知识库查询获得的资料，根据以上信息，回答下列问题:" + "\n" + prompt
            mix_result=self.Chat_base(question)
            return prompt,knowledge_result,web_search_v1_result,mix_result
        except Exception as err_mix:
            err_mix="[Error]" + str(err_mix)
            return prompt,knowledge_result,web_search_v1_result,err_mix
    
    def chat_no_search(self,prompt):
        web_search_v1_result=""
        knowledge_result = ""
        try: 
            no_search = self.Chat_base(prompt)
            return prompt,knowledge_result,web_search_v1_result, no_search
        except Exception as err_mix:
            err_mix="[Error]" + str(err_mix)
            return prompt,knowledge_result,web_search_v1_result,err_mix
            
    def cut_line(self,part):
        cut_line_diffrent_part = "~~~~~~~~~~~~~~~~~~~~~{part}~~~~~~~~~~~~~~~~~~~".format(part=part)
        return cut_line_diffrent_part
    
    def main_chat(self,prompt):
        self.web_search_v1_prompt = "联网查找与问题\"{prompt}\"相关的文档，请详细整理搜索的结果给我,可以给出适当的建议或方案，必要时解释文档的原理等，说详细就行不需要总结".format(prompt=prompt)
        
        
        
                
        if self.with_chroma_db_search and self.with_web_search:
            return self.cdb_web_search(prompt)
                
        elif self.with_web_search and not self.with_chroma_db_search:
            return self.web_search(prompt)
        elif not self.with_web_search and self.with_chroma_db_search:
            return self.cdb_search(prompt)
        elif not self.with_web_search and not self.with_chroma_db_search:
            return self.chat_no_search(prompt)
        else:
            raise ValueError("self.with_chroma_db_search and self.with_web_search must be type\"bool\"")
                
            
if __name__ == '__main__':
    test = Chat_All_Methods(with_web_search=False, with_history=False ,with_chroma_db_search=True, AI_url=Spark_deepthink, domain_type=domain_dt)
    question,zsk,lw,mix = test.main_chat("读书和休息怎么分配")
    #response = "~~~~~~~~~~~~~~~知识库查询结果~~~~~~~~~~~~~~~" + "\n" + zsk + "\n" +"~~~~~~~~~~~~~~~~~~~~~~~" + "\n" +"~~~~~~~~~~~~联网查询~~~~~~~~~~~~~~~" + "\n" + lw + "\n" + "~~~~~~~~~~~~~~~~~~~~~~~"+ "\n" +mix 
    response = mix
    print("Q:",question)
    print("\n")
    print("A:",response)
'''
# 初始化向量数据库
db_manager = ChromaDBManager()
file_paths = [str(path) for path in Path("documents").glob("*") if path.is_file()]

# 查询相似文档
query_text = "陆老师是谁"


# 删除文件
#db_manager.delete_by_source("file1.pdf")

# 清空数据库
#db_manager.clear_all()
'''
