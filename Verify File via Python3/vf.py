import os,hashlib

#Two Calculator Function
def calcSHA1(filepath):
	with open(filepath,'rb') as f:
		sha1obj = hashlib.sha1()
		sha1obj.update(f.read())
		return sha1obj.hexdigest()

def calcMD5(filepath):
	with open(filepath,'rb') as f:
		md5obj = hashlib.md5()
		md5obj.update(f.read())
		return md5obj.hexdigest()

class VFile():
	sha1 = None
	md5 = None

	def __init__(self,sourceFilePath):	
		self.sourceFilePath = sourceFilePath
		self.sha1 = calcSHA1(self.sourceFilePath)
		self.md5 = calcMD5(self.sourceFilePath)
	
	def compareFiles(self,targetFilePath,algorithm='sha1'):
		targetFile = VFile(targetFilePath)
		if algorithm == 'sha1':
			return targetFile.sha1 == self.sha1
		if algorithm == 'md5':
			return targetFile.md5 == self.md5
	
	def compareVerifystrings(self,targetVerifystring,algorithm='sha1'):
		if algorithm == 'sha1':
			return self.sha1 == targetVerifystring.lower()
		elif algorithm == 'md5':
			return self.md5 == targetVerifystring.lower()

#Smart Comparison Functon
def smartComparison(source,target):
	if os.path.isfile(source):
		sf = VFile(source)
		print('FilePath:',source)
		print('\tSHA1:',sf.sha1)
		print('\tMD5:',sf.md5)
		if os.path.isfile(target):
			tf = VFile(target)
			print('FilePath:',target)
			print('\tSHA1:',tf.sha1)
			print('\tMD5:',tf.md5)	
			#Two File Comparison(either sha1 or md5 is ok.)
			print('Identical:',str(sf.sha1==tf.sha1))
		else:
			#From 160bit bin string transfer to 40bit hex string
			#Not distinct UPPER/LOWER
			target = target.lower()
			print('Verify String:',target)		
			if len(target)==40:
				print('Identical:',str(sf.sha1==target))
			else:
				print('Identical:',str(sf.md5==target))
	else:
		source = source.lower()	
		print('Verify String:',source)
		if os.path.isfile(target):
			tf = VFile(target)
			print('FilePath:',target)
			print('\tSHA1:',tf.sha1)
			print('\tMD5:',tf.md5)	
			if len(source)==40:
				print('Identical:',str(source == tf.sha1))
			else:	
				print('Identical:',str(source == tf.md5))
		else:
			target = target.lower()
			print('Verify String:',target)
			print('Identical:',str(source == target))

if __name__ == '__main__':
	import sys
	if len(sys.argv)==3:
		print()
		print('Computing..')
		smartComparison(sys.argv[1],sys.argv[2])
	elif len(sys.argv)==2 and os.path.isfile(sys.argv[1]):
		print()
		print('Computing...')
		#Only one input as target.Use default source
		default_f = VFile('GB2312Text.txt')
		print('FilePath:GB2312Text.txt')
		print('\tSHA1:',default_f.sha1)
		print('\tMD5:',default_f.md5)		
		vf = VFile(sys.argv[1])
		print('FilePath:',sys.argv[1])
		print('\tSHA1:',vf.sha1)
		print('\tMD5:',vf.md5)
		retCode=default_f.compareFiles(sys.argv[1])
		print('Identical:',retCode)
		
