# -*- coding:utf-8 -*-

"""
Created on Mon Feb 27th 2017 12:13
@author : David
help : www.shiyanlou.com
事件驱动－－回调函数实现爬虫
"""

"""
## 非阻塞式IO，节省socket I/O阻塞时浪费的时间
sock = socket.socket()
sock.setblocking(False)
# 不是傻傻的一直等待，而是试一下，不在就过一会再来
try:
	sock.connect(('xkcd.com',80))
except BlockingIOError:
	pass

## 单线程上的多IO
from selectors import DefaultSelector,EVENT_WRITE
# C语言网络编程select函数－－不设置即处于阻塞状态，等待IO事件发生才被激活，然后告诉你socket上发生（读｜写｜异常）
# Python中也有select函数，还有更高效的poll,还有简单更好用的DefaultSelector
# 只需要将 非阻塞socket＋事件＋回调函数 绑定在一起就好
selector = DefaultSelector()

sock = socket.socket()
sock.setblocking(False)
try:
	sock.connect(('xcsd.com',80))
except BlockingIOError:
	pass

def connected():
	selector.unregister(sock.fileno())
	print('connected!')

# selector.register在socket的写事件上绑定了回调函数connected
# 该socket的 第一次 写事件标志着连接的建立，connected函数在连接建立成功后解除所有数据的绑定
selector.register(sock.fileno(),EVENT_WRITE,connected)

## 事件驱动
def loop():
	while True:	
		events =selector.select()
		# 不断获得IO事件
		for event_key,event_mask in events:
			# 遍历事件 并 调用相应处理（回调函数）
			callback = event_key.data
			callback()
"""

from selectors import *
import socket
import re
import urllib.parse
import time

urls_todo = set(['/'])
seen_urls = set(['/'])
#
concurrency_achieved = 0
selector = DefaultSelector()
stopped = False

class Fetcher:
	def __init__(self,url):	
		self.response = b''
		self.url = url
		self.sock = None
	
	#
	def fetch(self):
		global concurrency_achieved
		concurrency_achieved = max(concurrency_achieved, len(urls_todo))

		self.sock=socket.socket()
		self.sock.setblocking(False)
		try:
			self.sock.connect(('xkcd.com',80))
		except BlockIOError:
			pass
		selector.register(self.sock.fileno(),EVENT_WRITE,self.connected)

	#
	def connected(self,key,mask):
		print('connected!')
		#
		selector.unregister(key.fd)
		request = 'GET {} HTTP/1.0\r\nHost:xkcd.com\r\n\r\n'.format(self.url)
		self.sock.send(request.encode('ascii'))
		#
		selector.register(key.fd,EVENT_READ,self.read_response)

	#
	def read_response(self,key,mask):
		global stopped
		chunk = self.sock.recv(4096) #
		if chunk:
			self.response += chunk
		else:
			selector.unregister(key.fd)
			links = self.parse_links()

			#
			for link in links.difference(seen_urls):
				urls_todo.add(link)
				Fetcher(link).fetch()
	
			seen_urls.update(links)	
			urls_to.remove(self.url)
			if not urls_todo:
				stopped = True	#

	def body(self):
		body = self.response.split(b'\r\n\r\n', 1)[1]
		return body.decode('utf-8')

	def parse_links(self):
		if not self.response:
			print('error: {}'.format(self.url))
			return set()
		if not self._is_html():
			return set()
		urls = set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''',self.body()))

		links = set()
		for url in urls:
			normalized = urllib.parse.urljoin(self.url, url)
			parts = urllib.parse.urlparse(normalized)
			if parts.scheme not in ('', 'http', 'https'):
				continue
			host, port = urllib.parse.splitport(parts.netloc)
			if host and host.lower() not in ('xkcd.com', 'www.xkcd.com'):
				continue
			defragmented, frag = urllib.parse.urldefrag(parts.path)
			links.add(defragmented)

			return links

	def _is_html(self):
		head, body = self.response.split(b'\r\n\r\n', 1)
		headers = dict(h.split(': ') for h in head.decode().split('\r\n')[1:])
		return headers.get('Content-Type', '').startswith('text/html')


start = time.time()

# Begin fetching http://xkcd.com/353
fetcher = Fetcher('/353/')
fetcher.fetch()

# 
# def loop():
while not stopped:
	events = selector.select)
	for event_key,event_mask in events:
		callback = event_key.data		
		callback()
print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls), time.time() - start))







