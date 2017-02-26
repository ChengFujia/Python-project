# -*- coding:utf-8 -*-

"""
Created on Sun 26 Feb 2017 10:02
@author : David
Help : <500 lines>
实验一：线程池实现并发爬虫
"""
from queue import Queue 
from threading import Thread, Lock
import socket
import time
import urllib.parse
import re

"""
# socket抓取页面
def fetch(url):
	sock = socket.socket()
	sock.connect(('localhost.com',3000))
	request = 'GET {} HTTP/1.0\r\nHost:localhost\r\n\r\n'.format(url)
	sock.send(request.encode('ascii'))
	response = b''
	chunk = sock.receive(4096)
	while chunk:
		response += chunk
		chunk = sock.recv(4096)
	links = parse_links(response)
	q.add(links)

# 多线程
# 导入线程库
import threading
# 开启一个线程
t = 你新建的线程
t.start()	# 开启
t.join()	# 你的当前函数就阻塞在这一步，直到线程运行完，才能继续向下执行
# 通过函数创建线程
def funca():
	pass
t = threading.Thread(target = funca,name='自己取的名字')
# 通过继承类创建线程
class Fetcher(threading.Thread):
	def __init__(self):
		Thread.__init__(self)
		# 加这句之后，主程序退出，子线程也会跟着退出
		# 加这句之后，设置为后台进程，主程序退出之前不输出
		self.daemon = True
	def run(self):
		# 线程运行的函数
		pass
t = Fetcher()
# 多个线程竞争全局变量资源时候，需要上锁
lock = threading.Lock()
lock.acquire()	# 上锁
“操作全局变量”
lock.release()	# 解锁

# 多线程同步－－队列
# 导入队列类
from queue import Queue
# 创建队列，maxsize若为0意思默认无限大
q = Queue(maxsize = 0)
# 队列先进先出
q.put(item)	# 如果已满，阻塞
q.get(item)	# 如果为空，阻塞
q.join()	# 阻塞直到所有任务完成
q.task_done()	# 线程告知任务完成
"""

# 记录已经解析到的连接
seen_urls = set(['/'])
lock = Lock()

# 定义 线程类
class Fetcher(Thread):
	def __init__(self,tasks):
		Thread.__init__(self)
		# 任务队列
		self.tasks = tasks
		# 后台进程（不会直接输出）
		self.daemon = True
		# 开启线程
		self.start()

	def run(self):
		while True:
			url = self.tasks.get()
			print(url)
			sock = socket.socket()
			sock.connect(('localhost',3000))
			get = 'GET {} HTTP/1.0\r\nHost:localhost\r\n\r\n'.format(url)
			sock.send(get.encode('ascii'))
			response = b''
			chunk = sock.recv(4096)
			while chunk:
				response += chunk
				chunk = sock.recv(4096)

			# 解析页面上的所有链接
			links = self.parse_links(url,response)
			lock.acquire()	# 上锁
			# 得到的新链接加入任务队列和seen_urls中
			for link in links.difference(seen_urls):
				self.tasks.put(link)
			seen_urls.update(links)

			lock.release()	# 解锁
			# 通知任务队列这个线程的任务完成拉（只能在进程内部）
			self.tasks.task_done()

	def parse_links(self,fetched_url,response):
		if not response:
			print('error: {}'.format(fetched_url))
			return set()
		if not self._is_html(response):
			return set()

		# 通过href属性 找到所有链接
		urls = set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''',self.body(response)))
		links = set()
		for url in urls:
			# 可能找到的是相对路径，需要join一下；绝对路径直接返回
			normalized = urllib.parse.urljoin(fetched_url,url)
			# 分段存储url信息
			parts = urllib.parse.urlparse(normalized)
			if parts.scheme not in ('','http','https'):
				continue
			host,port = urllib.parse.splitport(parts.netloc)
			if host and host.lower() not in ('localhost'):
				continue
			# 有的界面会通过地址里面的#frag在页面内跳转，把这个去掉
			defragmented,frag = urllib.parse.urldefrag(parts.path)
			links.add(defragmented)
		return links

	# 得到报文的html部分
	def body(self,response):
		body = response.split(b'\r\n\r\n',1)[1]
		return body.decode('utf-8')

	# 判断是否为html
	def _is_html(self,response):
		head,body = response.split(b'\r\n\r\n',1)
		headers = dict(h.split(': ') for h in head.decode().split('\r\n')[1:])
		return headers.get('Content-Type','').startswith('text/html')

# 自定义线程池
class ThreadPool:
	def __init__(self,num_threads):
		self.tasks = Queue()
		for _ in range(num_threads):
			Fetcher(self.tasks)

	def add_task(self,url):
		self.tasks.put(url)

	def wait_completion(self):
		# 队列不为空，或者为空但是取得item的线程还未告知完成任务时，处于阻塞状态
		self.tasks.join()

"""
# 使用标准池中的线程池
from multiprocessing.pool import ThreadPool
#...省略掉中间部分...
#...去掉Fetcher初始化中的self.start()

使用ThreadTool时，处理的对象可以不是线程对象，实际上Fetcher的线程部分ThreadTool根本用不到
因为它自己内部已开了几个线程在等待任务输入。这里偷了个懒只删除了self.start()
实际上可以把Fetcher的线程部分都去掉

#...删除自己实现的ThreadTool...

if __name__ == '__main__':
	start = time.time()
	pool = ThreadPool()
	tasks = Queue()
	tasks.put('/')
	Workers = [Fetcher(tasks) for i in range(4)]
	# 这里活用了map函数（使用map_async）是防止这一步阻塞，阻塞留给下一步
	#　目的是把Fetcher和线程池中的线程分配好，线程自动调用run函数
	pools.map_async(lambda w:w.run(),Workers)
	tasks.join()
	pool.close()
	print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls),time.time()-start))
"""
if __name__ == "__main__":
	start = time.time()
	# 开四个进程
	pool = ThreadPool(4)
	# 从根地址开始抓起
	pool.add_task('/')
	pool.wait_completion()
	print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls),time.time()-start))
