#!/usr/bin/python
# encoding:utf-8

def lines(file):
	#'generator'
	for line in file:
		yield line
	yield '\n'

def blocks(file):
	block = []
	for line in lines(file):
		if line.strip():
			block.append(line)
		elif block:
			yield ''.join(block).strip()
			block = []
