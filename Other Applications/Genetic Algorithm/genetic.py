# 利用遗传算法解决一个函数最优化的Demo
from numpy import random
import numpy as np
import matplotlib.pyplot as plt
from math import pi,sin
import copy

class Gas():
	def __init__(self,popsize,chrosize,xrangemin,xrangemax):
		self.popsize = popsize      # 每代的个体数
		self.chrosize = chrosize    # 变量编码长度
		self.xrangemin = xrangemin  # 变量取值范围
		self.xrangemax = xrangemax
		self.crossrate = 1          # 交叉率
		self.mutationrate = 0.01    # 变异率

	# 初始化种群
	def initialpop(self):
		pop = random.randint(0,2,size=(self.popsize,self.chrosize))
		return pop

	# 原函数
	def fun(self,x1):
		return x1*sin(10*pi*x1) + 2.0
	# 由于这里取最大值，所以用函数值替代适应度函数
	def get_fitness(self,x):
		fitness = []
		for x1 in x:
			fitness.append(self.fun(x1))
		return fitness

	# 选择－－轮盘赌算法
	# 输入：上一代的种群，上一代的种群适应度 列表
	def selection(self,popsel,fitvalue):
		new_fitvalue = []
		totalfit = sum(fitvalue)
		accumulator = 0.0
		for val in fitvalue:
			# 对每一个适应度除以总的适应度，然后累加
			# 这样使得适应度大的个体获得更大的比例空间
			new_value = (val*1.0/totalfit)
			accumulator += new_value
			new_fitvalue.append(accumulator)
		ms = []
		for i in xrange(self.popsize):
			# 随机生成［0，1］之间的随机数
			ms.append(random.random())
		# 对随机数进行排序
		ms.sort()
		fitin = 0
		newin = 0
		newpop = popsel
		while newin < self.popsize:
			if(ms[newin] < new_fitvalue[fitin]):
				newpop[newin] = popsel[fitin]
				newin = newin +1
			else:
				fitin = fitin +1
		pop = newpop
		return pop

	# 交叉--单点交叉
	def crossover(self,pop):
		for i in xrange(self.popsize-1):
			# 近邻个体交叉，若随机数小于交叉率
			if(random.random() < self.crossrate):
				# 随机选择交叉点
				singpoint = random.randint(0,self.chrosize)
				temp1 = []
				temp2 = []
				# 对个体进行重组、切片
				temp1.extend(pop[i][0:singpoint])
				temp1.extend(pop[i+1][singpoint:self.chrosize])
				temp2.extend(pop[i+1][0:singpoint])
				temp2.extend(pop[i][singpoint:self.chrosize])
				pop[i] = temp1
				pop[i+1] = temp2
		return pop

	# 变异--基因/位反转
	def mutation(self,pop):
		for i in xrange(self.popsize):
			# 反转变异，随机数小于变异率，进行变异
			if (random.random() < self.mutationrate):
				mpoint = random.randint(0,self.chrosize-1)
				# 随机点上的基因进行反转
				if (pop[i][mpoint] == 1):
					pop[i][mpoint] = 0
				else:
					pop[i][mpoint] = 1
		return pop

	# 精英保护策略
	def elitism(self,pop,popbest,nextbestfit,fitbest):
		# 输入参数：变异之后的种群，上一代最优个体
		# 本代最优适应度，上一代的最优适应度
		if nextbestfit-fitbest <0:
			# 满足精英策略后，排到最差个体的索引，进行替换
			# 上一代的最优个体 替换 本来的最差个体
			pop_worst = nextfitvalue.index(min(nextfitvalue))
			pop[pop_worst] = popbest
		return pop

	# 对群组在实数空间内解码
	# 对十进制进行转换到求解空间中的数值
	def get_declist(self,chroms):
		step = (self.xrangemax - self.xrangemin)/float(2**self.chrosize-1)
		self.chroms_declist = []
		for i in xrange(self.popsize):
			chrom_dec = self.xrangemin + step*self.chromtodec(chroms[i])
			self.chroms_declist.append(chrom_dec)
		return self.chroms_declist

	# 二进制数组转化为十进制
	def chromtodec(self,chrom):
		m = 1
		r = 0
		for i in xrange(self.chrosize):
			r = r + m * chrom[i]
			m = m*2
		return r

if __name__ == '__main__':
	generation = 100			# 遗传代数 
	mainGas = Gas(100,10,-1,2)	# 初始化Gas类：种群大小，编码长度，变量范围
	pop = mainGas.initialpop()	# 种群初始化
	pop_best = []				# 每一代的最优个体
	for i in xrange(generation):
		# 在遗传代数中进行迭代
		declist = mainGas.get_declist(pop)			# 解码 
		fitvalue = mainGas.get_fitness(declist)		# 适应度函数
		popbest = pop[fitvalue.index(max(fitvalue))]# 找到适应度最高的个体
		popbest = copy.deepcopy(popbest)
		fitbest = max(fitvalue)
		pop_best.append(fitbest)					# 存储每代的最高适应度 值

		############################################# 进行算子操作，不断更新pop/种群
		mainGas.selection(pop,fitvalue)				# 选择
		mainGas.crossover(pop)						# 交叉
		mainGas.mutation(pop)						# 变异

		############################################# 进行精英保留之前的准备
		nextdeclist = mainGas.get_declist(pop)			# 本代结果的 解码
		nextfitvalue = mainGas.get_fitness(nextdeclist)	# 本代结果的 适应度函数
		nextbestfit = max(nextfitvalue)					# 本代结果的 最大适应度

		mainGas.elitism(pop,popbest,nextbestfit,fitbest)# 比较上一代和这一代

	t = [x for x in xrange(generation)]
	s = pop_best
	plt.plot(t,s)
	plt.show()
	plt.close()