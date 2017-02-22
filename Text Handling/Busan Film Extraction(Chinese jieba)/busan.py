#-*- coding:utf-8 -*-
import os,sys
import jieba,codecs,math
import jieba.posseg as pseg

# 基于共现提取《釜山行》人物关系
names = {}		#姓名辞典（姓名－出现次数）
relationships = {}	#关系辞典（起点－｛终点－权值｝）
lineNames = [] 		#每段内人物关系（lineNames[i]是一个列表）	

jieba.load_userdict("dict.txt")		#加载字典
with codecs.open("busan.txt","r","utf-8") as f:
	for line in f.readlines():
		poss = pseg.cut(line)	#分词并返回该词词性
		lineNames.append([])	#为新读入的一段添加人物名称列表
		for w in poss:
			#当分词长度小于2或者词性不是nr时 －> 非人名
			if w.flag != "nr" or len(w.word)<2:
				continue
			#最新加入的段落的人物名称列表 增加人物
			lineNames[-1].append(w.word)
			#更新人物出现次数
			if names.get(w.word) is None:
				names[w.word] = 0
				relationships[w.word] = {}
			names[w.word] +=1

#打印分词后的姓名结果
#for name,times in names.items():
#	print name,times

for line in lineNames:			#针对每一段
	for name1 in line:
		for name2 in line:	#针对每一段中任意的两个人
			if name1 == name2:
				continue
			if relationships[name1].get(name2) is None:
				relationships[name1][name2] = 1		#这个很有趣，python实现二维数组
			else:
				relationships[name1][name2] += 1

with codecs.open("busan_node.txt",'w','gbk') as f:
	f.write("Id Label Weight\r\n")
	for name,times in names.items():
		f.write(name + " "+name+" "+str(times) + "\r\n")
with codecs.open("busan_edge.txt",'w','gbk') as f:
	f.write("Source Target Weight\r\n")
	for name,edges in relationships.items():
		for v,w in edges.items():
			if w>3:
				f.write(name+" "+v+" "+str(w)+"\r\n")





		
