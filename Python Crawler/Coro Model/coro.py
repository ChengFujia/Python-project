# -*- coding:utf-8 -*-
"""
Created on Tue 28 Feb 2017 15:55
@author:David
help:www.shiyanlou.com
事件驱动--协程实现爬虫
"""

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

## 2.使用yield from分解协程
# 一旦连接成功，我们会发送GET请求到服务器等待响应，之前这些工作在不同回调函数中实现，现在可以放在同一个生成器函数中
def fetch(self):
	# ...省略之前的连接部分...
	sock.send(request.encode('ascii'))
	while True:
		f = Future()
		def on_readable():
			f.set_result(sock.recv(4096))
		selector.register(sock.fileno(),EVENT_READ,on_readable)
		chunk = yield f
		selector.unregister(sock.fileno())
		if chunk:
			self.response += chunk
		else:
			break

# 虽然采用yield使代码集中于生成器函数，但随着回调函数增多，代码量增加
# 因此考虑yield from分解代码(分解子协程，重构代码)
# 实现read协程接受一个数据块
def read(sock):
	f = Future()
	def on_readable():
		f.set_result(sock.recv(4096))
	selector.register(sock.fileno(),EVENT_READ,on_readable)
	chunk = yield f
	selector.unregister(sock.fileno())
	return chunk

# 实现read_all协程接受整个消息
def read_all(sock):
	response = []
	chunk = yield from read(sock)
	while chunk:
		response.append(chunk)
		chunk = yield from read(sock)
	return b''.join(response)

# 现在fetcher中调用read_all
def fetch(self):
	# ...省略之前的连接部分...
	sock.send(request.encode('ascii'))
	self.response = yield from read_all(sock)

# 将yield和yield from有效统一起来	
def __iter__(self):
	yield self
	return self.result
"""

from selectors import *
import socket
import re
import urllib.parse
import time

class Future:
	def __init__(self):
		self.result = None
		self._callbacks = []

	def result(self):
		return self.result
	
	def add_done_callback(self,fn):
		self._callbacks.append(fn)

	def set_result(self,result):
		self.result = result
		for fn in self._callbacks:
			fn(self)
	
	def __iter__(self):
		yield self
		return self.result

class Task:
	def __init__(self,coro):
		self.coro = coro
		f = Future()
		f.set_result(None)
		self.step(f)

	def step(self,future):
		try:
			next_future = self.coro.send(future.result)
		except StopIteration:
			return
		next_future.add_done_callback(self.step)

urls_seen = set(['/'])
urls_todo = set(['/'])
concurrency_achieved = 0
selector = DefaultSelector()
stopped = False

def connect(sock,address):
	f = Future()
	sock.setblocking(False)
	try:
		sock.connect(address)
	except BlockingIOError:
		pass

	def on_connected():
		f.set_result(None)
	selector.register(sock.fileno(),EVENT_WRITE,on_connected)
	yield from f
	selector.unregister(sock.fileno())

def read(sock):
	f = Future()
	def on_readable():
		f.set_result(sock.recv(4096))
	selector.register(sock.fileno(),EVENT_READ,on_readable)
	chunk = yield f
	selector.unregister(sock.fileno())
	return chunk

# 实现read_all协程接受整个消息
def read_all(sock):
	response = []
	chunk = yield from read(sock)
	while chunk:
		response.append(chunk)
		chunk = yield from read(sock)
	return b''.join(response)

class Fetcher:
	def __init__(self,url):
		self.response = b''
		self.url = url

	def fetch(self):
		global concurrency_achieved,stopped
		concurrency_achieved = max(concurrency_achieved,len(urls_todo))

		sock = socket.socket()
		yield from connect(sock,('localhost',3000))
		get = 'GET {} HTTP/1.0\r\nHost: localhost\r\n\r\n'.format(self.url)
		sock.send(get.encode('ascii'))
		self.response = yield from read_all(sock)

		self._process_response()
		urls_todo.remove(self.url)
		if not urls_todo:
			stopped = True
		print(self.url)

	def body(self):
		body = self.response.split(b'\r\n\r\n', 1)[1]
		return body.decode('utf-8')

	def _process_response(self):
		if not self.response:
			print('error: {}'.format(self.url))
			return
		if not self._is_html():
			return
		urls = set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''',self.body()))

		for url in urls:
			normalized = urllib.parse.urljoin(self.url, url)
			parts = urllib.parse.urlparse(normalized)
			if parts.scheme not in ('', 'http', 'https'):
				continue
			host, port = urllib.parse.splitport(parts.netloc)
			if host and host.lower() not in ('localhost'):
				continue
			defragmented, frag = urllib.parse.urldefrag(parts.path)
			if defragmented not in urls_seen:
				urls_todo.add(defragmented)
				urls_seen.add(defragmented)
				Task(Fetcher(defragmented).fetch())

	def _is_html(self):
		head, body = self.response.split(b'\r\n\r\n', 1)
		headers = dict(h.split(': ') for h in head.decode().split('\r\n')[1:])
		return headers.get('Content-Type', '').startswith('text/html')

if __name__ == '__main__':
	start = time.time()
	fetcher = Fetcher('/')
	Task(fetcher.fetch())

	while not stopped:
		events = selector.select()
		for event_key,event_mask in events:
			callback = event_key.data
			callback()

	print('{} URLs fetched in {:.1f} seconds, achieved concurrency = {}'.format(len(urls_seen), time.time() - start, concurrency_achieved))                             










