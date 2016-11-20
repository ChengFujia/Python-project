#coding=utf8
import jieba
import codecs
import random
import re

class Markov:
	def __init__(self, filepath = None, mode = 0, coding="utf8"):
		self.dictLen = 0		# 前缀字典长度
		self.Cap = []			# 可作为语句开始词语的集合
		self.mode = mode		# 模式 中文为1 英文为0
		self.coding = coding	# 编码方式
		self.dic = {}			# 前缀字典
		if filepath is not None:
			self.train(filepath, mode, coding)
	def train(self, filepath = '', mode = 0, coding="utf8"):		# 训练
		self.dic = {}
		self.Cap = []
		self.mode = mode
		self.coding = coding				# 初始化
		if filepath is None or filepath == '':
			return							# 违例判断
		eg_puncmark = re.compile('[\,\.\!\;\?\~\`\#\$\%\@\^&\*\(\)\]\[]')	# 英文标点正则
		zh_puncmark = re.compile('[，。！；]')								# 中文标点正则
		with codecs.open(filepath, "r", coding) as f:
			for line in f.readlines():
				words = []
				line = re.sub('[\r\n]', "", line)							# 清除行末回车
				if mode == 0:												# 英文模式
					sentences = eg_puncmark.split(line)						# 按标点划分语句
					sentences_words = []
					for sentence in sentences:								# 按空格划分单词并过滤空串
						sentences_words.append(filter(lambda x:x != '',sentence.split(" ")))
					for words in sentences_words:							# 对每句中的单词
						for i in range(len(words)-2):
							keypair = words[i] + " " + words[i+1]			# 将两个词拼接为前缀
							if keypair[0].isupper():						
								# 若前缀首字母为大写则添加到可作为开头的前缀集合中
								self.Cap.append(keypair)
							if self.dic.get(keypair) is None:
								self.dic[keypair] = [words[i+2]]
							else:
								# 为该前缀添加后缀
								self.dic[keypair].append(words[i+2])
				else:														# 中文模式
					sentences = zh_puncmark.split(line)						# 按中文标点划分
					for sentence in sentences:
						jwords = jieba.cut(sentence, cut_all=False)			# 对每句做中文分词
						for word in jwords:
							if len(word) >= 2:
								words.append(word)							# 仅考虑长度大于2的中文词语
						if len(words) > 2:
							self.Cap.append(words[0] + " " + words[1])		# 添加该每句开头的两个词
							words = filter(lambda x:x != '', words)			# 过滤空串
							for i in range(len(words)-2):
								keypair = words[i] + " " + words[i+1]		# 组建前缀
								if self.dic.get(keypair) is None:
									self.dic[keypair] = [words[i+2]]
								else:
									# 为该前缀添加后缀
									self.dic[keypair].append(words[i+2])
			# 更新前缀字典长度
			self.dictLen = len(self.dic)
	def getDic(self):
		return self.dic
	def say(self, length = 10):
		if self.dictLen <= 2:			# 字典长度不足以构建文本
			print("I feel tired and I need food to say something.")
		else:
			keypair = self.Cap[random.randint(0, len(self.Cap)-1)]		# 随机选取可作为语句开头的前缀
			fst, snd = keypair.split(" ")[0], keypair.split(" ")[1]		# 将前缀按空格拆分为词语
			pairlen = len(self.dic[keypair])
			if self.mode == 0:
				sentence = fst + " " + snd
			else:
				sentence = fst + snd 									# 中文间无空格
			while length > 0 and pairlen > 0:
				temp = self.dic[keypair][random.randint(0, pairlen-1)]	# 随机选取后缀词语
				fst = snd
				snd = temp
				if self.mode == 0:
					sentence = sentence + " " + snd
				else:
					sentence = sentence + snd
				keypair = fst + " " + snd 								# 更新待搜索前缀
				if self.dic.get(keypair) is not None:
					pairlen = len(self.dic[keypair])
				else:
					break
				length -= 1
			if self.mode == 0:
				print sentence + "."
			else:
				print sentence + "。".decode("utf8")					# 需为中文标点解码再输出
