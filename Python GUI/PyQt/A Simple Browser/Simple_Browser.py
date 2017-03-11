#-*- coding:utf-8 -*-
"""
Created on Sat 11th March 2017 17:47
@author : David
QtWebKit 实现简易浏览器
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebKitWidgets import *

import sys

class MainWindow(QMainWindow):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		# 设置窗口标题
		self.setWindowTitle('My Browser')
		# 设置窗口图片
		self.setWindowIcon(QIcon('icons/penguin.png'))
		self.show()
		
		## 三.增加标签栏
		self.tabs = QTabWidget()
		# 3.2. 增加了 双击导航栏 生成新浏览器窗口的事件
		self.tabs.setDocumentMode(True)
		self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
		self.tabs.currentChanged.connect(self.current_tab_changed)
		# 3.3. 增加了 浏览器窗口 关闭选项
		self.tabs.setTabsClosable(True)
		self.tabs.tabCloseRequested.connect(self.close_current_tab)
		self.add_new_tab(QUrl('http://www.shiyanlou.com'),'Homepage')
		self.setCentralWidget(self.tabs)

		new_tab_action = QAction(QIcon('icons/add_page.png'),'New Page',self)
		new_tab_action.triggered.connect(self.add_new_tab)
		'''
		## 单一的浏览器窗口
		self.browser = QWebView()
		# 默认的url
		url = "http://www.shiyanlou.com/faq"
		# 设置为当前页面
		self.browser.setUrl(QUrl(url))
		# 置于窗口中间位置
		self.setCentralWidget(self.browser)
		'''
		## 二.增加导航栏和地址栏
		# 2.1.增加导航栏
		navigation_bar = QToolBar('Navigation')
		# 设置图标大小
		navigation_bar.setIconSize(QSize(16,16))
		self.addToolBar(navigation_bar)
		# 定义导航栏的诸多按钮
		back_button = QAction(QIcon('icons/back.png'),'Back',self)
		next_button = QAction(QIcon('icons/next.png'),'Forward',self)
		stop_button = QAction(QIcon('icons/cross.png'),'stop',self)	
		reload_button = QAction(QIcon('icons/renew.png'),'reload',self)	
		## 四.增加导航栏按钮 直接返回主界面
		home_button = QAction('Home',self)
		# 绑定按钮事件/槽
		back_button.triggered.connect(self.tabs.currentWidget().back)
		next_button.triggered.connect(self.tabs.currentWidget().forward)
		stop_button.triggered.connect(self.tabs.currentWidget().stop)
		reload_button.triggered.connect(self.tabs.currentWidget().reload)
		home_button.triggered.connect(self.return_home)
		# 将button增加到toolbar中
		navigation_bar.addAction(back_button)
		navigation_bar.addAction(next_button)
		navigation_bar.addAction(stop_button)
		navigation_bar.addAction(reload_button)
		navigation_bar.addAction(home_button)

		# 2.2.增加地址栏
		self.urlbar = QLineEdit()
		# 设置成 输入地址，按enter，直接跳向该目标
		self.urlbar.returnPressed.connect(self.navigate_to_url)
		navigation_bar.addSeparator()
		navigation_bar.addWidget(self.urlbar)
		#self.browser.urlChanged.connect(self.renew_urlbar)

	# 返回主界面
	def return_home(self):
		self.add_new_tab(QUrl('http://www.shiyanlou.com/faq'),'Return Home')

	# 响应回车enter按钮
	def navigate_to_url(self):
		q = QUrl(self.urlbar.text())
		if q.scheme() == '':
			q.setScheme('http')
		self.tabs.currentWidget().setUrl(q)

	def renew_urlbar(self,q,browser=None):
		# 如果不在当前 浏览器窗口，不响应
		if browser != self.tabs.currentWidget():
			return
		# 将当前网页的链接更新到地址栏
		self.urlbar.setText(q.toString())
		self.urlbar.setCursorPosition(0)

	# 3.1.重构了browser，将多个browser放在tabs中
	def add_new_tab(self,qurl=QUrl(''),label='Blank'):
		# 创建浏览器窗口
		browser = QWebView()
		browser.setUrl(qurl)
		i = self.tabs.addTab(browser,label)
		self.tabs.setCurrentIndex(i)
		browser.urlChanged.connect(lambda qurl,browser=browser:self.renew_urlbar(qurl,browser))

		# 加载完毕后，将标签标题修改为网页相关的标题
		browser.loadFinished.connect(lambda _,i=i,browser=browser:
			self.tabs.setTabText(i,browser.page().mainFrame().title()))

	# 双击导航栏事件
	def tab_open_doubleclick(self,i):
		if i == -1:
			self.add_new_tab()

	# 切换标签/浏览器窗口
	def current_tab_changed(self,i):
		qurl = self.tabs.currentWidget().url()
		self.renew_urlbar(qurl,self.tabs.currentWidget())

	# 关闭标签
	def close_current_tab(self,i):
		# 如果只剩下一个，则不关闭
		if self.tabs.count() < 2:
			return 
		self.tabs.removeTab(i)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()