#-*- coding:utf-8 -*-
import os
import sys
from bs4 import BeautifulSoup
import markdown

class MarkdownToHtml:
	headTag = '<head><meta charset="utf-8"  /></head>'
	
	def __init__(self,cssFilePath=None):
		if cssFilePath != None:
			self.genStyle(cssFilePath)
	
	def genStyle(self,cssFilePath):
		#Regular file operation
		#f=open(cssFilePath,'r')
		#cssString=f.read()
		#f.close()

		#Senior file operation--auto close
		with open(cssFilePath,'r') as f:
			cssString = f.read()
		#- means from end to begin
		self.headTag = self.headTag[:-7] + '<style type="text/css">{}</style>'.format(cssString)+self.headTag[-7:]

	def markdownToHtml(self,sourceFilePath,destinationDirectory=None,outputFileName=None):
		if not destinationDirectory:
			destinationDirectory = os.path.dirname(os.path.abspath(sourceFilePath))

		if not outputFileName:
			#basename--full file name,eg:1.txt
			#splittext-->['1','txt']
			outputFileName = os.path.splitext(os.path.basename(sourceFilePath))[0]+'.html'

		if destinationDirectory[-1] != '/':
			destinationDirectory += '/'

		#MarkDown text--utf8  Windows CMD--gbk (Avoiding coding error)
		with open(sourceFilePath,'r',encoding='utf8') as f:
			markdownText = f.read()
		rawHtml = self.headTag + markdown.markdown(markdownText,output_format='html5')
		#beautifulHtml = BeautifulSoup(rawHtml,'html5lib').prettify()
		with open(destinationDirectory+outputFileName,'w',encoding='utf8') as f:
			f.write(rawHtml)
			#f.write(beautifulHtml)

#Make sure codes after "if ..." don't run when this module is import
if __name__ == '__main__':
	mth = MarkdownToHtml()
	argv = sys.argv[1:]
	#Accept command:
	#python3 mth.py source1.md [source2.md,[source3.md...]] [-s cssFilePath] [-o outputDirectory]
	outputDirectory = None
	if '-s' in argv:
		cssArgIndex = argv.index('-s')+1
		cssFilePath = argv[cssArgIndex]
		#Test whether cssFilePath is valid
		if not os.path.isfile(cssFilePath):
			print('Invalid Path: %s',cssFilePath)
			sys.exit()
		mth.genStyle(cssFilePath)
		#POP order must not reverse
		argv.pop(cssArgIndex)
		argv.pop(cssArgIndex-1)
	if '-o' in argv:
		dirArgIndex = argv.index('-o')+1
		outputDirectory = argv[dirArgIndex]
		#Test whether outputDirectory is valid
		if not os.path.isdir(outputDirectory):
			print('Invalid Directory: %s',outputDirectory)
		#POP order must not reverse
		argv.pop(dirArgIndex)
		argv.pop(dirArgIndex-1)
	#Now,the remaining in argv[] are all sourcepath
	for filePath in argv:
		if os.path.isfile(filePath):
			mth.markdownToHtml(filePath,outputDirectory)
		else:
			print('Invalid Path: '+filePath)
