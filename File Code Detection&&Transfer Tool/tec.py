#-*- coding:utf-8 -*-
import sys
import os
import argparse
from chardet.universaldetector import UniversalDetector

#使用argparse模块解析命令行参数（初始化解析器＋添加属性）
parser = argparse.ArgumentParser(description = '文本文件编码检测与转换')
parser.add_argument('filePaths',nargs='+',help='检测或转换的文件路径')
parser.add_argument('-e','--encoding',nargs='?',const='UTF-8',help='''
目标编码。支持的编码有：
ASCII,(Default) UTF-8 (with or without a BOM),UTF-16 (with a BOM),UTF-32 (with a BOM),Big5,GB2312/GB19030,EUC-TW,
HZ-GB-2312,ISO-2022-CN,EUC-JP,SHIFT_JIS,ISO-2022-JP,ISO-2022-KR,KOI8-R,MacCyrillic,IBM855,IBM866,ISO-8859-5,
windows-1251,ISO-8859-2,windows-1250,EUC-KR,ISO-8859-5,windows-1251,ISO-8859-1,windows-1252,ISO-8859-7,
windows-1253,ISO-8859-8,windows-1255,TIS-620''')
parser.add_argument('-o','--output',help='输出目录')

#使用parser解析器对象 真正解析参数－－自动调用sys.argv获取参数
args = parser.parse_args()
#特殊参数情况处理
if args.output != None:
	if not args.encoding:
		args.encoding = 'UTF-8'
	if not os.path.isdir(args.output):
		print('Invalid Directory:'+args.output)
		sys.exit()
	else:
		if args.output[-1] != '/':
			args.output += '/'

#实例化一个通用检测器
detector = UniversalDetector()
print()
print('Encoding (Confidence)',':','File path')
#遍历文件路径
for filePath in args.filePaths:
	if not os.path.isfile(filePath):
		print('Invalid Path:'+ filePath)	
		continue
        detector.reset()
        for each in open(filePath,'rb'):
                #检测器读取数据
                detector.feed(each)
                #检测完成则跳出循环
                if detector.done:
                        break
        detector.close()
        charEncoding = detector.result['encoding']
        confidence = detector.result['confidence']
        if charEncoding is None:
                charEncoding = 'Unknown'
                confidence = 0.99
        print('{}{:>12}:{}'.format(charEncoding.rjust(8)，'('+str(confidence*100)+'%)',filePath))

        #读取源文本文件
        if args.encoding and charEncoding != 'Unknown' and confidence >0.6:
                with open(filePath,'r',encoding=charEncoding,errors='replace') as f:
                        temp = f.read()

                #写入目标文本文件
                outputPath = args.output + os.path.basename(filePath) if args.output else filePath
                with open(outputPath,'w',encoding=args.encoding,errors='replace') as f:
                        f.write(temp)

