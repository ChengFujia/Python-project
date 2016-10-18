import sys
import os
import time
import threading
import termios
import tty
import cv2
import pyprind

class CharFrame:
	ascii_char = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

	#pixel to char
	def pixelToChar(self,luminance):
		return self.ascii_char[int(luminance/(256/len(ascii_char)))]

	#frame convert
	#img is image object;limitSize is list
	def convert(self,img,limitSize=-1,fill=False,wrap=False):
		if limitSize != -1 and (img.shape[0] > limitSize[1] or img.shape[1] > limitSize[0]):
			img = cv2.resize(img,limitSize,interpolation=cv2.INTR_AREA)
		ascii_frame =  ''
		blank = ''
		if fill:
			blank += ' '*(limitSize[0]-img.shape[1])
		if wrap:
			blank += '\n'
		for i in range(img.shape[0]):		#num line
			for j in range(img.shape[1]):	#num column
				ascii_frame += self.pixelToChar(img[i,j])
			ascii_frame += blank
		return ascii_frame

class I2Char(CharFrame):
	result = None
	def __init__(self,path,limitSize=-1,fill=False,wrap=False):
		self.genCharImage(self,path,limitSize=-1,fill=False,wrap=False)

	#generate character image
	def genCharImage(self,path,limitSize=-1,fill=False,wrap=False):
		#open a file with cv2(OpenCV)
		img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
		if img is None:
			return
		self.result = self.convert(img,limitSize,fill,wrap)
	
	def show(self,stream = 2):
		if self.result is None:
			return
		#fileno() = file describer
		#os.isatty(fd) = bool,when file is open and connects to a tty is TRUE
		if stream == 1 and os.isatty(sys.stdout.fileno()):
			self.streamOut = sys.stdout.write
			self.streamFlush = sys.stdout.flush
		elif stream == 2 and os.isatty(sys.stderr.fileno()):
			self.streamOut = sys.stderr.write
			self.streamFlush = sys.stderr.flush
		elif hasattr(stream,'write'):
			self.streamOut = stream.write	
			self.streamFlush = stream.flush
		self.streamOut(self.result)
		self.streamFlush()
		self.streamOut('\n')

class V2Char(CharFrame):
	def __init__(self,path):
		if path.endswith('txt'):	#after export() -> .txt
			self.load(path)
		else:				#video file -> .video
			self.genCharVideo(path)

	def genCharVideo(self,filepath):
		self.charVideo = []
		#open a video with cv2(OpenCV)
		cap = cv2.VideoCapture(filepath)
		self.timeInterval = round(1/cap.get(5),3)	#confirm gap time between two frames
		nf = int(cap.get(7))				#get num of frame
		print('Generate char video,please wait...')
		for i in pyprind.prog_bar(range(nf)):	
			rawFrame = cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2GRAY)
			frame = self.convert(rawFrame,os.get_terminal_size(),fill=True)
			self.charVideo.append(frame)
		cap.release()
	
	def play(self,stream = 1):
		if not self.charVideo:
			return
		if stream == 1 and os.isatty(sys.stdout.fileno()):
			self.streamOut = sys.stdout.write
			self.streamFlush = sys.stdout.flush
		elif stream == 2 and os.isatty(sys.stderr.fileno()):
			self.streamOut = sys.stderr.write
			self.streamFlush = sys.stderr.flush	
		elif hasattr(stream,'write'):
			self.streamOut = stream.write
			self.streamFlush = stream.flush
		old_settings = None
		breakflag = None
		#standard input file describer
		fd = sys.stdin.fileno()
		
		def getChar():
			nonlocal breakflag
			nonlocal old_settings
			#save standard input attribute
			old_settings = termios.tcgetattr(fd)
			#set standard input raw
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
			breakflag = True if ch else False
		
		getchar = threading.Threat(target = getChar)
		getchar.daemon = True
		getchar.start()
		rows = len(self.charVideo[0])//os.get_terminal_size()[0]
		for frame in self.charVideo:
			if breakflag is True:
				break
			self.streamOut(frame)
			self.streamFlush()
			time.sleep(self.timeInterval)
			#return to begin 
			self.streamOut('\033[{}A\r'.format(rows-1))
		#recover standard input
		termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)
		#go to last
		self.streanOut('\033[{}B\033[K'.format(rows-1))
		#clear the screen
		for i range(rows-1):
			self.streamOut('\033[1A')
			self.streamOut('\r\033[K')
		info = 'User interrupt!\n' if breakflag else 'Finished!\n'
		self.streamOut(info)			
	











