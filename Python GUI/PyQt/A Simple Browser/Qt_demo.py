# -*- coding:utf-8 -*-
"""
Created on Fri 10th March 2017 13:21
@author:David
QT基础
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys

# 实现常规的对话框
class CustomDialog(QDialog):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.setWindowTitle('New Dialog')
		# 添加按钮选项
		QBtn = QDialogButtonBox.Ok|QDialogButtonBox.Cancel
		buttonBox = QDialogButtonBox(QBtn)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		layout = QVBoxLayout()
		layout.addWidget(buttonBox)
		self.setLayout(layout)

# 实现色块
class Color(QWidget):
	def __init__(self,color,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.setAutoFillBackground(True)

		# 调色板
		palette = self.palette()
		palette.setColor(QPalette.Window,QColor(color))
		self.setPalette(palette)	

class MainWindow(QMainWindow):
	## 实现自定义信号
	my_signal = pyqtSignal(str)

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		## 关于布局
		self.setWindowTitle('My First App')
		colors = ['red','green','blue','yellow','black']
		layout = QGridLayout()
		for i,color in enumerate(colors):
			for j in range(len(colors)):
				layout.addWidget(Color(color),i,j)
		widget = QWidget()
		widget.setLayout(layout)
		self.setCentralWidget(widget)
		"""
		## 关于QWidget控件
		self.setWindowTitle('My First App')
		layout = QVBoxLayout()
		# 包含丰富的派生控件
		widgets = [QCheckBox,QComboBox,QDateTimeEdit,QDial,QDoubleSpinBox,QFontComboBox,QLCDNumber,QLineEdit,
				QProgressBar,QPushButton,QRadioButton,QSlider,QSpinBox,QTimeEdit]
		for item in widgets:
			layout.addWidget(item())
		widget = QWidget()
		widget.setLayout(layout)
		self.setCentralWidget(widget)
		"""

		## 关于工具栏
		tb = QToolBar('Tool Bar')
		# 设置图表大小
		tb.setIconSize(QSize(16,16))
		# 增加工具栏
		self.addToolBar(tb)
		# 添加按钮动作，并加载图像
		button_action = QAction(QIcon('icons/penguin.png'),'New Dialog',self)
		# 设置按钮动作相关
		button_action.setStatusTip('This is a new Dialog')
		button_action.triggered.connect(self.onButtonClick)
		button_action.setCheckable(True)
		# 添加到工具栏
		tb.addAction(button_action)
		
		## 关于菜单栏
		mb = self.menuBar()
		# 关闭默认菜单栏
		mb.setNativeMenuBar(False)
		# 增加菜单项
		file_menu = mb.addMenu('&File')
		# 绑定动作
		file_menu.addAction(button_action)
		# 新增二级菜单的 按钮动作
		button_action2 = QAction('C++',self)
		button_action3 = QAction('Python',self)
		button_action2.setCheckable(True)
		button_action3.setCheckable(True)
		button_action2.triggered.connect(self.onButtonClick)
		button_action3.triggered.connect(self.onButtonClick)
		# 增加分割线
		file_menu.addSeparator()
		# 增加二级目录项
		build_menu = file_menu.addMenu('&Build System')
		build_menu.addAction(button_action2)
		build_menu.addSeparator()
		build_menu.addAction(button_action3)
		# 设置状态栏
		self.setStatusBar(QStatusBar(self))
		
		self.setWindowTitle('My First App')
		button = QPushButton('Click me')
		button.pressed.connect(self._click_button)
		self.my_signal.connect(self._my_func)
		self.setCentralWidget(button)
		
		"""
		##  信号与槽
		# self.windowTitleChanged.connect(self._my_func)
		# 在上一句基础上的高级绑定，不显示APP名称
		self.windowTitleChanged.connect(lambda x:self._my_func('David',666))
		##	多按钮的直观表达
		# 水平布局
		layout = QHBoxLayout()
		# 生成五个按钮
		for i in range(5):
			button = QPushButton(str(i))
			# 每个按钮绑定事件
			button.pressed.connect(lambda x=i:self._my_func1(x))
			# 增加按钮到本布局
			layout.addWidget(button)
		# 生成窗口部件
		widget = QWidget()
		# 设置窗口布局
		widget.setLayout(layout)
		# 将窗口置于GUI中
		self.setCentralWidget(widget)
		"""

		"""
		# 设置窗口标题
		self.setWindowTitle('My First App')
		# 设置标签
		label = QLabel('Welcome...')
		#
		label.setAlignment(Qt.AlignCenter)
		self.setCentralWidget(label)
		"""
	# 按钮点击事件（弹出对话框）
	def onButtonClick(self,s):
		dlg = CustomDialog(self)
		dlg.exec_()

	# 点击按钮事件
	def _click_button(self):
		# 发送自定义信号
		self.my_signal.emit('David')

	# 点击按钮事件
	def _my_func1(self,n):
		print('click button %s'%n)
	
	# 点击按钮事件
	def _my_func(self,s='my_func',a=100):
		dic = {'s':s,'a':a}
		print(dic)

# 创建应用实例
app = QApplication(sys.argv)
# 创建窗口实例
window = MainWindow()
# 窗口显示
window.show()
# 执行应用，进入事件循环
app.exec_()
