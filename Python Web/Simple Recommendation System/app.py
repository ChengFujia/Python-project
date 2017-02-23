# -*- coding:utf-8 -*-
"""
Created on Thu Feb 23 19:50 2017
@author: David
Help:www.shiyanlou.com
Flask实现推荐系统后台
"""

from flask import Flask,render_template,request
import recommend
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')
@app.route('/search/')
def search():
	# request为全局变量，可以用来得到用户输入信息
	n = request.args.get('user')
	# 调用推荐算法
	dic = recommend.recommend(n)
	# 利用返回结果 进行 模板渲染
	return render_template('search.html',Data=dic)

if __name__ == "__main__":
	app.run(debug=True)
