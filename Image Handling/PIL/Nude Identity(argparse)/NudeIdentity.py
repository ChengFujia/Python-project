# -*- coding:utf-8 -*-

"""
Created on Fri Feb 24 13:28 2017
@author: David
Help:www.shiyanlou.com
Python3色情图片识别
"""

import sys
import os
import _io
from collections import namedtuple
from PIL import Image

class Nude(object):
	# 定义一个类型Skin -- 针对每一个像素点的类
	Skin = namedtuple("Skin","id skin region x y")

	# 读取图片实例，设置各个全局变量
	def __init__(self,path_or_image):
		# 若是一个图片实例，直接赋值
		if isinstance(path_or_image,Image.image):
			self.image = path_or_image
		# 若是一个路径，读取到实例中
		elif isinstance(path_or_image,str):
			self.image = Image.open(path_or_image)

		# 获得图片的所有颜色通道
		bands = self.image.getbands()
		# 如果是单通道（灰度图），将它转换成RGB模式
		if len(bands) == 1:
			# 同样大小新建图片实例
			new_img = Image.new("RGB",self.image.size)
			# 拷贝 灰度图self.image 到 RGB图new_img,PIL自动进行颜色通道转换
			new_img.paste(self.image)
			f = self.image.filename
			# 替换self.image，文件路径覆盖 实质上
			self.image = new_img
			self.image.filename = f

		# 存储对应图片 所有像素 的全部Skin对象
		self.skin_map = []
		# 检测到的皮肤区域，元素的索引就是皮肤区域号，元素都是一些Skin对象的列表
		self.detected_regions = []
		# 元素都是包含一些int对象（区域号）的列表
		# 这些元素中的区域号都是待整合的区域
		self.merge_regions = []
		# 整合后的皮肤区域，元素的索引就是皮肤区域号，元素都是一些Skin对象的列表
		self.skin_regions = []
		# 最近合并的两个皮肤区域的区域号
		self.last_from,self.last_to = -1,-1
		# 色情图像判断结果
		self.result = None
		# 处理得到的信息
		self.message = None
		# 图像的宽高
		self.width,self.height = self.image.size
		# 图像的总像素数
		self.total_pixels = self.width * self.height

	# 图片越大，耗费资源越多，因此调整大小
	def resize(self,maxwidth=1000,maxheight=1000):
		"""
		基于最大宽高按照比例重设图片大小
		注意：这可能会影响检测算法的结果

		如果无变化返回0
		原宽度大于maxwidth的返回1
		原高度大于maxheight的返回2
		原宽高大于maxwidth maxheight的返回3

		maxwidth maxheight 传参数时可通过False值来忽略
		"""
		# 存储返回值
		ret = 0
		if maxwidth:
			if self.width > maxwidth:
				wpercent = (maxwidth / self.width)
				hsize = int(self.height * wpercent)
				fname = self.image.filename
				# 重采样滤波器，用于抗锯齿
				self.image = self.image.resize((maxwidth,hsize),Image.LANCZOS)
				self.image.filename = fname
				self.width,self.height = self.image.size
				self.total_pixels = self.width * self.height
				ret += 1
		if maxheight:
			if self.height > maxheight:
            			hpercent = (maxheight / float(self.height))
			        wsize = int((float(self.width) * float(hpercent)))
            			fname = self.image.filename
            			self.image = self.image.resize((wsize, maxheight), Image.LANCZOS)
            			self.image.filename = fname
            			self.width, self.height = self.image.size
            			self.total_pixels = self.width * self.height
            			ret += 2
    		return ret

	def parse(self):
		# 如果已经有结果了，返回本对象
		if self.result is not None:
			return self
		# 获得图片所有像素数据
		pixels = self.image.load()

		for y in range(self.height):
			for x in range(self.width):
				# 得到像素的RGB三个通道的值
				# ［x,y］ = [(x,y)]
				r = pixels[x,y][0]
				g = piexls[x,y][1]
				b = pixels[x,y][2]
				# 判断当前像素是否为肤色
				isSkin = True if self._classify_skin(r,g,b) else False
				# 给每一个像素分配唯一id，从1，2， ... ，height*width
				# 注意x,y从0开始的
				_id = x+ y*self.width +1
				# 为每一个像素点创建Skin对象，并添加到列表中
				self.skin_map.append(self.Skin(_id,isSkin,None,x,y))
				
				# 如果不是肤色像素，直接跳出，下次循环
				if not isSkin:
					continue
				# 否则，检查相邻像素，进行处理
				# _id从1开始的，而索引从0开始的
				check_indexes = [_id -2 ,		# 左边的像素
						_id - self.width -2,	# 左上边的像素
						_id - self.width -1,	# 上边的像素
						_id - self.width ]	# 右上边的像素
				# 用来记录肤色像素所在的区域号，初始化为－1，无意义的
				region = -1
				# 遍历每一个相邻像素的索引
				for index in check_indexes:
					# 尝试索引相邻像素的Skin对象，没有则跳出循环
					try:
						self.skin_map[index]
					except IndexError:
						break
					# 如果相邻像素是肤色像素
					if self.skin_map[index].skin:
						# 如果相邻像素和当前像素的region均为有效值
						# 且二者不同，且尚未添加相同的合并任务
						if (self.skin_map[index].region != None and
							region != None and region != -1 and 
							self.skin_map[index].region != region and
							self.last_from != region and
							self.last_to != self.skin_map[index].region):
							# 那么完成这两个像素点的合并工作
							self._add_merge(region,self.skin_map[index.region])
						# 记录该相邻像素所在的区域号
						region = self.skin_map[index].region

				# 遍历完所有相邻像素后，若region仍等于－1，说明所有相邻的都不是肤色像素
				if region == -1:
					# 更改属性为新的区域号，注意元组是不可变类型，不能直接更改属性
					_skin = self.skin_map[_id-1]._replace(region=len(self.detected_regions))
					self.skin_map[_id-1] = _skin
					# 将此肤色像素所在区域创建为新区域
					self.detected_regions.append([self.skin_map[_id-1]])
				# 若region不等于－1且不等于None，说明有区域是有效值的相邻肤色像素
				elif region != None:
					# 将此像素的区域号更改为与相邻像素相同
					_skin = self.skin_map[_id-1]._replace(region=region)
					self.skin_map[_id-1] = _skin
					# 向这个区域的像素列表中增加此像素
					self.detected_regions[region].append(self.skin_map[_id-1])
				
		# 完成所有区域的合并任务，合并整理后的区域存储到self.skin_regions
		self._merge(self.detected_regions,self.merge_regions)
		# 分析皮肤区域，得到判定结果
		self._analyse_regions()
		return self

	# 基于像素的肤色检测技术
	def _classify_skin(self,r,g,b):
		# 根据 RGB 值判定
		rgb_classifier = r > 95 and \
        		g > 40 and g < 100 and \
        		b > 20 and \
        		max([r, g, b]) - min([r, g, b]) > 15 and \
        		abs(r - g) > 15 and \
        		r > g and \
        		r > b
    		
		# 根据处理后的 RGB 值判定
    		nr, ng, nb = self._to_normalized(r, g, b)
    		norm_rgb_classifier = nr / ng > 1.185 and \
        		float(r * b) / ((r + g + b) ** 2) > 0.107 and \
        		float(r * g) / ((r + g + b) ** 2) > 0.112

    		# HSV 颜色模式下的判定
    		h, s, v = self._to_hsv(r, g, b)
    		hsv_classifier = h > 0 and \
        		h < 35 and \
        		s > 0.23 and \
       			s < 0.68

    		# YCbCr 颜色模式下的判定
    		y, cb, cr = self._to_ycbcr(r, g,  b)
    		ycbcr_classifier = 97.5 <= cb <= 142.5 and 134 <= cr <= 176

    		# 效果经实践分析
    		# return rgb_classifier or norm_rgb_classifier or hsv_classifier or ycbcr_classifier
    		return ycbcr_classifier

	# 颜色模式转化
	def _to_normalized(self, r, g, b):
    		if r == 0:
        		r = 0.0001
    		if g == 0:
        		g = 0.0001
    		if b == 0:
        		b = 0.0001
    		_sum = float(r + g + b)
    		return [r / _sum, g / _sum, b / _sum]

	def _to_ycbcr(self, r, g, b):
    		# http://stackoverflow.com/questions/19459831/rgb-to-ycbcr-conversion-problems
    		y = .299*r + .587*g + .114*b
    		cb = 128 - 0.168736*r - 0.331364*g + 0.5*b
    		cr = 128 + 0.5*r - 0.418688*g - 0.081312*b
    		return y, cb, cr

	def _to_hsv(self, r, g, b):
    		h = 0
    		_sum = float(r + g + b)
    		_max = float(max([r, g, b]))
    		_min = float(min([r, g, b]))
    		diff = float(_max - _min)
    		if _sum == 0:
        		_sum = 0.0001
		if _max == r:
        		if diff == 0:
            			h = sys.maxsize
        		else:
            			h = (g - b) / diff
    		elif _max == g:
        		h = 2 + ((g - r) / diff)
    		else:
        		h = 4 + ((r - g) / diff)

    		h *= 60
    		if h < 0:
        		h += 360

    		return [h, 1.0 - (3.0 * (_min / _sum)), (1.0 / 3.0) * _max]

	# 对self.merge_regions操作，增加到列表中
	def _add_merge(self,_from,_to):
		# 两个区域号赋值给类属性
		self.last_from = _from
		self.last_to = _to
		# 记录from索引值，初始化为－1
		from_index = -1
		# 记录to索引值，初始化为－1
		to_index = -1

		# 遍历每一个元素（列表）
		for index,region in enumerate(self.merge_regions):
			# 遍历每一个列表中的区域号
			for r_index in region:
				if r_index == _from:
					from_index = index
				if r_index == _to:
					to_index = index

		# 若两个区域号码都在
		if from_index != -1 and to_index != -1:
			# 且在两个不同集合中，则合并
			if from_index != to_index:
				self.merge_regions[from_index].extend(self.merge_regions[to_index])
				del(self.merge_regions[to_index])
			return 

		# 若两个都不在
		if from_index == -1 and to_index == -1:
			# 则生成一个新的区域号
			self.merge_regions.append([_from,_to])
			return 

		# 若只有一个在
		if from_index != -1 and to_index == -1:
			# 将不在的合并到在的列表中
			self.merge_regions[from_index].append(_to)
			return 

		# 若只有一个在
		if from_index == -1 and to_index != -1:
			# 将不在的合并到在的列表中
			self.merge_regions[to_index].append(_from)
			return 

	# 将self.merge_regions中的元素中的区域号所代表的区域合并，得到新的皮肤区域列表
	def _merge(self,detected_regions,merge_regions):
		# 列表元素是包含一些代表像素的Skin对象的列表
		# 列表元素代表的是皮肤区域，元素索引为区域号
		new_detected_regions = []
		
		# 将merge_regions中的元素中的区域号代表的区域合并
		for index,region in enumerate(merge_regions):
			try:
				new_detected_regions[index]
			except IndexError:
				new_detected_regions.append([])
			for r_index in region:
				new_detected_regions[index].extend(detected_regions[r_index])
				# 将合并后的清空
				detected_regions[r_index] = []

		# 添加剩下的（未经过合并的）其余皮肤区域到new_detected_regions中
		for region in detected_regions:
			if len(region) > 0:
				new_detected_regions.append(region)

		# 清理 new_detected_regions
		self._clear_regions(new_detected_regions)

	# 只保留像素数量大于指定数量的皮肤区域
	def _clear_regions(self,detected_regions):
		for region in detected_regions:
			if len(region) > 30:
				self.skin_regions.append(region)
		
		
				
