#-*- coding:utf-8 -*-
import random
import itertools
from copy import deepcopy

# Default:every part is 3*3
def make_board(m=3):
	# A list contains all 1-9
	numbers = list(range(1,m**2+1))
	# board is 2d list..
	board = None
	while board is None:
		# Attempt to fill..
		board = attempt_board(m,numbers)
		# Only board is filled can the loop ends
	return board

def attempt_board(m,numbers):
	n = m**2
	# init
	board = [[None for _ in range(n)] for _ in range(n)]
	# i->(0,8)    j->(0,8)   one by one
	for i,j in itertools.product(range(n),repeat=2):
		# i==row j==column
		# (i0,j0) is start location
		# left-up corner
		i0,j0 = i-i%m,j-j%m

		# Shuffle is to make random as outer loop is same eachtime
		random.shuffle(numbers)
		for x in numbers:
			# not in same row + not in same column + not in same 3*3
			if (x not in board[i] and all(row[j] !=x for row in board) and all(x not in row[j0:j0+m] for row in board[i0:i])):
				board[i][j] = x
				# If there is one suitable, then break inner loop
				# Continue outer loop
				break
		# for..else..
		# enless all 9 numbers don't suit
		else:
			return None
	return board

def print_board(board,m=3):
	numbers = list(range(1,m**2+1))
	# each row make <=5 random None
	# omit controls None numbers // game challange level
	omit = 5	
	challange = deepcopy(board)	# just value, not object
	# At most omit * (m**2) None
	# maybe some duplicate..
	for i,j in itertools.product(range(omit),range(m**2)):
		# Get one random of numbers
		x = random.choice(numbers) - 1
		challange[x][j] = None

	# Print : UI
	spacer = "++-----+-----+-----++-----+-----+-----++-----+-----+-----++"
	print (spacer.replace('-','='))
	# Make to enum: {0:row0{},...8:row8{}}
	for i,line in enumerate(challange):
		# *() == A tuple
		print("||  {}  |  {}  |  {}  ||  {}  |  {}  |  {}  ||  {}  |  {}  |  {}  ||".format(*(cell or ' ' for cell in line)))
		if (i+1)%3 ==0 :
			print(spacer.replace('-','='))
		else:
			print(spacer)
	return challange

def print_answers(board):
	# Print all numbers..
	spacer = "++-----+-----+-----++-----+-----+-----++-----+-----+-----++"
	print (spacer.replace('-','='))
	# Use original board.. without any changes
	for i,line in enumerate(board):
		print("||  {}  |  {}  |  {}  ||  {}  |  {}  |  {}  ||  {}  |  {}  |  {}  ||".format(*(cell or ' ' for cell in line)))
		if (i+1)%3 ==0 :
			print(spacer.replace('-','='))
		else:
			print(spacer)

Board = make_board()
print_board(Board)
