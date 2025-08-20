from models import *  # 纯属开发这本人懒，要想优化自己找哪些要导入
import re
import json

class AIchangetimetable:
    def __init__(self, json_input: json = None, temperature: float = 0.8, max_tokens: int = 8192):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.json_input = json_input
        
    def json2text(self, json_data: json = None) -> str:
        if json_data is None:
            json_data = self.json_input
        # 筛选出所有以"task"开头的键并排序
        task_keys = [key for key in json_data if re.match(r'^task\d+$', key)]
        # 按task后的数字进行排序
        sorted_keys = sorted(task_keys, key=lambda x: int(re.findall(r'\d+', x)[0]))
        
        # 生成对应文本行
        result_lines = []
        for key in sorted_keys:
            # 提取task后的数字（如task3提取3）
            task_num = re.findall(r'\d+', key)[0]
            result_lines.append(f"任务{task_num}:{json_data[key]}")
        # 拼接所有行并返回
        return '\n'.join(result_lines)
        
    def text2json(self, text: str = None):
        if text is None:
            text = self.result
        
        # 按行分割文本
        lines = text.strip().split('\n')
        
        # 构建结果字典
        result_dict = {}
        task_count = 1
        rest_count = 1
        
        # 提取关键优化点部分
        reason_start = None
        for i, line in enumerate(lines):
            if "关键优化点" in line or "优化建议" in line or "建议" in line:
                reason_start = i
                break
        
        # 分离任务/休息和优化点
        schedule_lines = lines[:reason_start] if reason_start is not None else lines
        reason_text = '\n'.join(lines[reason_start:]) if reason_start is not None else ""
        
        # 解析任务和休息
        for line in schedule_lines:
            line = line.strip()
            if not line:
                continue
                
            # 匹配任务
            task_match = re.match(r'任务(\d+):(.+)', line)
            if task_match:
                task_num = task_match.group(1)
                task_content = task_match.group(2).strip()
                result_dict[f"task{task_num}"] = task_content
                continue
                
            # 匹配休息
            rest_match = re.match(r'休息:?(?:休息)?\s*(\d+)\s*分钟', line)
            if rest_match:
                rest_duration = rest_match.group(1)
                result_dict[f"rest{rest_count}"] = f"休息{rest_duration}分钟"
                rest_count += 1
                continue
                
            # 如果既不是任务也不是休息，可能是其他格式的休息
            alt_rest_match = re.match(r'.*休息.*(\d+).*分钟', line)
            if alt_rest_match:
                rest_duration = alt_rest_match.group(1)
                result_dict[f"rest{rest_count}"] = f"休息{rest_duration}分钟"
                rest_count += 1
        
        return json.dumps(result_dict, ensure_ascii=False), reason_text
        
    def time_table_maker(self, text: str) -> str:
        prompt = f'''
下面是我一天的任务计划:
~~~~~~~~~~~~~~~~任务计划~~~~~~~~~~~~~~~~~
{text}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
请根据健康高效的原则，任务顺序可以调换(比如文理交替,即文科理科任务交叉安排，尽量不要连着做)，帮我重新排任务顺序并向内穿插休息的时间

注意:
1. 休息时间标注多长时间
2. 回答格式形如:
   任务1:xxx
   休息:休息xx分钟
   任务2:xxx
   休息:休息xx分钟
   任务3:xxx
   ...
3. 严格按我格式且不要遗漏任务
4. 在最后添加"**关键优化点**："并说明你的优化理由和建议
        '''
        
        AI_model = Chat_All_Methods(with_web_search=True, with_history=False, with_chroma_db_search=True, AI_url=Spark_deepthink, domain_type=domain_dt)
        question, zsk, lw, mix = AI_model.main_chat(prompt)    
        self.result = mix
        json_out, reason = self.text2json()
        return json_out, reason
    
    def proccess_main(self):
        text_input = self.json2text()
        json_out, reason = self.time_table_maker(text_input)
        return json_out, reason
        
if __name__ == '__main__':
    json_input = {
        "task1": "写数学作业",
        "task2": "开编程会议",
        "task3": "写代码",
        "task4": "电竞",
        "task5": "写物理作业",
        "task6": "写语文作业",
        "task7": "写英语作业",
    }
    print("传入json",json_input)
    test = AIchangetimetable(json_input)
    jsonout, reason = test.proccess_main()
    print("json版安排:", jsonout)
    print("原因:", reason)
    del test
