import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
try:
    from lib.config import appid, api_key, api_secret, Spark_lite, domain_lite, Spark_deepthink, domain_dt
except:
    from config import appid, api_key, api_secret, Spark_lite, domain_lite, Spark_deepthink, domain_dt
import websocket  # 使用websocket_client
import os
os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'
os.environ['SSL_CERT_FILE'] = '/etc/ssl/certs/ca-certificates.crt'

# 管理对话历史，按序编为列表
def getText(role, content, history):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    history.append(jsoncon)
    return history

# 获取对话中的所有角色的content长度
def getlength(history):
    length = 0
    for content in history:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

# 判断长度是否超长，当前限制8K tokens
def checklen(history):
    while (getlength(history) > 8000):
        del history[0]
    return history

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        return url

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)

# 收到websocket关闭的处理
def on_close(ws, one, two):
    pass

# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))

def run(ws, *args):
    data = json.dumps(gen_params(
        appid=ws.appid,
        domain=ws.domain,
        question=ws.question,
        temperature=ws.temperature,
        max_tokens=ws.max_tokens
    ))
    ws.send(data)

# 收到websocket消息的处理
def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        text = choices['text'][0]

        # 使用实例变量代替全局变量
        if 'reasoning_content' in text and text['reasoning_content']:
            reasoning_content = text["reasoning_content"]
            ws.isFirstcontent = True

        if 'content' in text and text['content']:
            content = text["content"]
            if ws.isFirstcontent:
                ws.answer += "\n*******************以上为思维链内 容，模型回复内容如下********************\n"
            ws.answer += content
            ws.isFirstcontent = False

        if status == 2:
            ws.close()

# 修复：添加缺失的temperature和max_tokens参数
def gen_params(appid, domain, question, temperature, max_tokens):
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234",
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data

def main(appid, api_key, api_secret, Spark_url, domain, question, temperature=1.2, max_tokens=32768):
    wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()

    # 创建WebSocket实例并添加自定义属性
    ws = websocket.WebSocketApp(
        wsUrl,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )

    # 添加实例变量代替全局变量
    ws.answer = ""
    ws.isFirstcontent = False
    ws.appid = appid
    ws.question = question
    ws.domain = domain
    ws.temperature = temperature
    ws.max_tokens = max_tokens

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return ws.answer  # 返回结果

class Common_Chat_Api:
    def __init__(self, appid=appid, api_secret=api_secret, api_key=api_key,
                 domain=domain_lite, url=Spark_lite, temperature=1.2, max_tokens=32768):
        self.appid = appid
        self.api_secret = api_secret
        self.api_key = api_key
        self.domain = domain
        self.Spark_url = url
        self.history = []  # 每个实例自己的对话历史
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(self, query):
        question = checklen(getText("user", query, self.history))
        result = main(
            self.appid,
            self.api_key,
            self.api_secret,
            self.Spark_url,
            self.domain,
            question,
            self.temperature,
            self.max_tokens
        )
        getText("assistant", result, self.history)
        return result

    # 修复：正确的方法名 clear_history
    def clear_history(self):
        self.history.clear()

    def check_history(self):
        return self.history

if __name__ == '__main__':
    test1 = Common_Chat_Api()
    test2 = Common_Chat_Api()

    response1 = test1.chat("你好！")
    print('------------------------------------------------')
    print(response1)
    print('------------------------------------------------')
    print(test1.check_history())
    print('------------------------------------------------')

    response2 = test2.chat("你好！")
    print('------------------------------------------------')
    print(response2)
    print('------------------------------------------------')
    print(test2.check_history())
    print('------------------------------------------------')

    # 修复：调用正确的方法名 clear_history
    test1.clear_history()
    response1 = test1.chat("请告诉我，我问的上一个问题是什么")
    print(response1)
    print('------------------------------------------------')
    print(test1.check_history())
