#coding=utf8
import requests
import itchat

KEY = '8edce3ce905a4c1dbb965e6b35c3834d'

#调用 图灵机器人 -> 将消息传给机器人，并返回机器人自动回复消息
def get_response(msg):
    apiUrl = "http://www.tuling123.com/openapi/api"
    data = {
        'key'	: KEY,
        'info'	: msg,
        'userid': 'wechat-robot',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        #字典的get方法 在没有text字段时会返回None，而不是异常
        return r.get('text')
    #若服务器没能正常响应（返回非json或者无法连接时），发生异常
    except:
        return

#调用 itchat接口 -> 接管微信消息，并将传给机器人
@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    defaultReply = "I received: " + msg['Text']
    reply = get_response(msg['Text'])
    #若reply非空，返回reply；否则，返回默认输出
    return reply or defaultReply

#采用热启动--修改程序而不用多次扫码
itchat.auto_login(hotReload=True)
itchat.run()
