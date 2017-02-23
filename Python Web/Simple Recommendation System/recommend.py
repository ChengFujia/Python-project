# -*- coding:utf-8 -*-
"""
Created on Thu Feb 23 14:53 2017
@author: David
Help: www.shiyanlou.com
实现番剧推荐的简单推荐算法
"""

from random import choice
import MySQLdb

def recommend(user):
	# 连接数据库
	DB = MySQLdb.connect("localhost",'root','','recommend')
	c = DB.cursor()

	# 下面的代码为实现从数据库中得到用户所喜欢的番剧编号，以便判断重复
	love = []
	sql = "select anime_id from user_anime where user_id=%s"%user
	c.execute(sql)
	# 抓取结果集
	results = c.fetchall()
	for line in results:
		love.append(line[0])

	# 下面的代码为实现思路1＋2,从数据库中根据用户喜爱的编号分析最贴切的标签top3
	sql = """
		select style_id from
		(select user_id,style_id from
			(select user_id,anime_id as id from user_anime where user_id=%s) as s
			natural join anime natural join
			(select anime_id as id,style_id from anime_style) as n
		)as temp group by style_id order by count(user_id) desc limit 3;
		"""%user
	c.execute(sql)
	results = c.fetchall()
	lis = []
	anime = {}
	for (line,) in results:
		lis.append(line)
	for i in lis:
		# 从番剧信息的数据库中得到Top3的各个类别的所有剧的id存入anime字典中
		sql = "select anime_id from anime_style where style_id="+str(i)+";"
		c.execute(sql)
		results = c.fetchall()
		anime_lis = []
		for result in results:
			anime_lis.append(result[0])
		# 键－值对，键是 标签id
		anime[str(i)] = anime_lis
	
	# 取Top3的交集 作为推荐集合
	s = set(anime[str(lis[0])])& set(anime[str(lis[1])]) & set(anime[str(lis[2])])

	loveSet = set(love)
	# 若太小了，扩大（仅仅使用一个标签）
	if loveSet > s:
		s = set(anime[str(lis[0])])

	# 把集合转换为列表，等待随机函数使用
	set_lis = []
	for i in s:
		set_lis.append(i)
	recommend = choice(set_lis)
	# 随机，直到出现没有看过的
	while recommend in love:
		recommend = choice(set_lis)
	
	# 得到推荐信息，返回等待使用，显示
	dic = {}
	sql = "selet name,brief from anime where id=%s;"%str(recommend)
	c.execute(sql)
	results = c.fetchall()
	dic['name'] = results[0][0]
	dic['brief'] = results[0][1]

	DB.close()
	return dic
