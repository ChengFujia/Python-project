# -*- coding:utf-8 -*-
"""
Created on Tue 28 Feb 2017 15:55
@author:David
help:www.shiyanlou.com
事件驱动--协程实现爬虫
"""

## 1.生成器实现协程模型
# 专门用来存储将要发给协程的信息的类
class Future:
	def __init__(self):
		self.result = None
		self._callbacks = []
	
	def add_done_callback(self,fn):
		self._callbacks.append(fn)

	# 当future对象调用该函数时从挂机状态变成激活状态，并运行注册了的回调函数
	def set_result(self,result):
		self.result = result
		for fn in self._callbacks:
			fn(self)

# 改造之前Fetcher中从fetch到connected的函数，加入Future和yield
class Fetcher:
	# 生成器函数，yield他来暂停fetch的运行直到连接建立，之后才继续运行
	def fetch(self):
		sock = socket.socket()
		sock.setblocking(False)
		try:
			sock.connect(('localhost',3000))
		except BlockingIOError:
			pass
	
		# 把 连接建立后 的部分也放了进来
		f = Future()
		def on_connected():
			# 连接建立后 通过set_result协程继续从yield的地方往下运行
			f.set_result(None)
		selector.register(sock.fileno(),EVENT_WRITE,on_connected)
		yield f
		selector.unregister(sock.fileno())
		print('connected!')

# 解决 set_result时运行的回调函数是哪里来的 相关问题
class Task:
	def __init__(self,coro):
		# 协程
		self.coro = coro

		# 创建并初始化一个为None的Future对象
		f = Future()
		f.set_result(None)

		# 步进一次（发送一次信息）
		# 在初始化时发送是为了协程到达第一个yield的位置，也是为了注册下一次的步进
		self.step(f)

	# 回调函数
	def step(self,future):
		try:
			# 向协程发送消息并得到下一个从协程那yield到的Future对象
			next_future = self.coro.send(future.result)
		except StopIteration:
			return

	# 新得到的Future对象上注册了step函数
	next_future.add_done_callback(self.step)

fetcher = Fetcher('/')
# 执行过程
# 1.为fetcher.fetch()（协程/生成器函数）初始化Task对象，并初始化内容为None -- Line53-54
# 2.向fetcher.fetch()（协程/生成器函数）发送None信息 -- Line58-64
# 3.则fetcher.fetch()（协程/生成器函数）才开始执行，从头到第一个yield,生成新的Future对象 -- Line28-37
# 4.新对象返回给next_future，然后新对象上注册了step函数 -- Line64-69
# 5.等待后面事件触发，又开始发送消息，协程再次执行 -- Line41-38
Task(fetcher.fetch())
loop()










