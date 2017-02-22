#-*- coding:utf8 -*-
from PIL import Image
import hashlib
import time
import math

# python 破解验证码（向量空间搜索引擎）

class VectorCompare:
	#计算矢量大小
	def magnitude(self,concordance):
		total = 0
		for word,count in concordance.iteritems():
			total += count ** 2
		return math.sqrt(total)
	#计算矢量之间的cos值
	def relation(self,concordance1,concordance2):
		relevance = 0
		topvalue = 0
		for word,count in concordance1.iteritems():
			if concordance2.has_key(word):
				topvalue += count * concordance2[word]
		return topvalue/(self.magnitude(concordance1)*self.magnitude(concordance2))

#根据图片生成矢量
def buildvector(im):
	d1 = {}
	count = 0
	#矢量的维度/坐标是每一个像素点的值
	for i in im.getdata():
		d1[count] = i
		count += 1
	return d1

v = VectorCompare()
iconset =['0','1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k',
'l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

imageset = []
import os
#导入训练集
for letter in iconset:
	for img in os.listdir('./iconset/%s/'%(letter)):
		temp = []
		if img != "Thumbs.db" and img != ".DS_Store":
			temp.append(buildvector(Image.open("./iconset/%s/%s"%(letter,img))))
		imageset.append({letter:temp})


im = Image.open("captcha.gif")
#将图片转化为8位像素模式(0-255)
im.convert("P")

'''
#打印颜色直方图
#print im.histogram()
his = im.histogram()
values = {}

for i in range(256):
	values[i] = his[i]

#对values进行排序，方向是反转（大－小），关键字是values.items()[1]
for j,k in sorted(values.items(),key=lambda x:x[1],reverse = True)[:10]:
	print j,k
'''

im2 = Image.new("P",im.size,255)		#相当于白画布
for x in range(im.size[1]):
	for y in range(im.size[0]):
		pix = im.getpixel((y,x))
		#重点关注的红色和灰色
		if pix == 220 or pix == 227:
			im2.putpixel((y,x),0)	#将相应点设置为黑色
#im2.save("captcha2.png")

inletter = False
foundletter = False
start = 0
end = 0
letters = []
#将验证码图片拆分成单字符
for y in range(im2.size[0]):
	for x in range(im2.size[1]):
		pix = im2.getpixel((y,x))
		if pix != 255:
			inletter = True
	if foundletter == False and inletter == True:
		foundletter = True
		start = y
	if foundletter == True and inletter == False:
		foundletter = False
		end = y
		letters.append((start,end))
	inletter = False
#print letters

'''
count = 0
for letter in letters:
	m = hashlib.md5()
	#从原图中剪切（x1,y1,x2,y2）
	im3 = im2.crop((letter[0],0,letter[1],im2.size[1]))
	#更新hash对象以字符串参数 ： m.update(a); m.update(b) is equivalent to m.update(a+b).
	m.update("%s%s"%(time.time(),count))
	im3.save("./%s.gif"%(m.hexdigest()))
	count += 1
'''

count = 0
for letter in letters:
	m = hashlib.md5()
	#从原图中剪切（x1,y1,x2,y2）
	im3 = im2.crop((letter[0],0,letter[1],im2.size[1]))
	guess = []
	
	for image in imageset:
		for x,y in image.iteritems():
			if len(y) != 0:
				guess.append((v.relation(y[0],buildvector(im3)),x))
	guess.sort(reverse = True)
	print "",guess[0]
	count += 1
