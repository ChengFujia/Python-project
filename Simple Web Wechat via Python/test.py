#-*- coding:utf-8
import itchat

@itchat.msg_register(itchat.content.TEXT)
def print_content(msg):
	#print(msg['Text'])             #在命令行输出 别人发给我的信息
	return msg['Text']              #自动回复 别人发给我的信息 原话返回 

itchat.auto_login(hotReload=True)       #一次登录
#itchat.auto_login()                    #多次登录
itchat.run()                            #保持在后台运行，开启服务，类似于网页版微信


'''
#调用 itchat 手动点对点发消息
import itchat
itchat.auto_login()
itchat.send(u'测试消息发送','filehelper')  #手动回复
'''

'''
#调用 图灵机器人 实现自动回复
import requests

apiurl = "http://www.tuling123.com/openapi/api"
data = {
	'key'	:'8edce3ce905a4c1dbb965e6b35c3834d',
	'info'	:'hello',
	'userid':'wechat-robot',
}

r = requests.post(apiurl,data=data).json()
print(r)
'''
