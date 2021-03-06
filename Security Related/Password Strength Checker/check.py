#-*- coding:utf-8 -*-
import re
import json

__all__ = ['password']

NUMBER = re.compile(r'[0-9]')
LOWER_CASE = re.compile(r'[a-z]')
UPPER_CASE = re.compile(r'[A-Z]')
OTHERS = re.compile(r'[^0-9a-zA-Z]')

def load_common_password():
	words = []
	with open('10k_most_common.txt','rb') as f:
		for word in f.readlines():
			# erase space (rstrip() && lstrip())
			words.append(word.strip())
	return words

COMMON_WORDS = load_common_password()

class Strength:
	def __init__(self,valid,strength,message):
		self.valid = valid
		self.strength = strength
		self.message = message
	def __repr__(self):
		#return self.message
		return self.strength
	def __str__(self):
		return self.message
		#return self.strength
	def __bool__(self):
		return self.valid

class Password:
	TERRIBLE = 0
	SIMPLE = 1
	MEDIUM = 2
	STRONG = 3
	
	# Attention: these two method don't have (self,) ,just (paragrams)
	# staticmethod: only run in class not in object..return a value
	# classmethod : only run in class not in object..return a object/class
	
	@staticmethod
	def is_common(input):
		return input in COMMON_WORDS

	@staticmethod
	def is_regular(input):
		reverse = input[::-1]
		regular = "".join(['qwertyuiop','asdfghjkl','zxcvbnm'])
		return input in regular or reverse in regular

	@staticmethod
	def is_by_step(input):
		delta = ord(input[1]) - ord(input[0])
		for i in range(2,len(input)):
			if ord(input[i]) - ord(input[i-1]) != delta:
				return False
		return True

	# magic method -- make class to function. aha..
	def __call__(self,input,min_length=6,min_types=3,level=STRONG):
		if len(input) < min_length:
			return Strength(False,'terrible','Password Too Short.')
		if self.is_regular(input) or self.is_by_step(input):
			return Strength(False,'simple','Password Has Regular.')
		if self.is_common(input):
			return Strength(False,'simple','Password Is Common.')

		types = 0;
		if NUMBER.search(input):
			types += 1
		if LOWER_CASE.search(input):
			types += 1
		if UPPER_CASE.search(input):
			types += 1
		if OTHERS.search(input):
			types += 1

		if types < 2:
			return Strength(level < self.SIMPLE,"simple","Password Too Simple.")
		if types < min_types:
			return Strength(level < self.MEDIUM,"medium","Password Not Strong Enough.")

		return Strength(True,'strong','Password Perfect.')

class email_:
	def __init__(self,address,ttype,valid):
		self.address = address
		self.type = ttype
		self.valid = valid
	def __repr__(self):
		if self.valid:
			return "True"
		else:
			return "False"

class Email:
	'''
	def __init__(self,email):
		self.email = email
	def isValiEmail(self):
		#pattern = re.compile(r'adc@qq.com')
		pattern = re.compile(r'[a-zA-Z0-9]+@[a-zA-Z0-9]+\.com')
		if pattern.search(self.email):
			return True
		else:
			return False
	def getEmailType(self):
		if self.isValiEmail():
			loc = self.email.find(r'@')
			leng = len(self.email)
			return self.email[loc+1:leng-4]
		else:
			return "Your email is wrong."
	'''
	@staticmethod
	def isValiEmail(input):
		pattern = re.compile(r'[a-zA-Z0-9]+@[a-zA-Z0-9]+.com')
		return pattern.search(input)
	@staticmethod	
	def getEmailType(input):
		loc = input.find(r'@')
		leng = len(input)
		return input[loc+1:leng-4]
	
	def __call__(self,input):
		if self.isValiEmail(input):
			type = self.getEmailType(input)	
			if type != 'qq':
				return False
			e = email_(input,type,True)
			return e
		else:
			return False
email = Email()
password = Password()
