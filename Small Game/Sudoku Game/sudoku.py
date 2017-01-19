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

def is_full(challange,m=3):
	# Ending...
	for i,j in itertools.product(range(m**2),repeat=2):
		if challange[i][j] is None:
			return False
	return True

def cal_candidate(challange,x,y,m=3):
	# values to be filled..
	candidate = range(1,m**2+1)
	for i in range(m**2):
		# row
		if challange[x][i] in candidate:
			candidate.remove(challange[x][i])
		# column
		if challange[i][y] in candidate:
			candidate.remove(challange[i][y])
	for i,j in itertools.product(range(m),repeat=2):
		# start location in 3*3
		x0,y0 = x-x%m,y-y%m
		if challange[x0+i][y0+j] in candidate:
			candidate.remove(challange[x0+i][y0+j])
	return candidate

def least_candidate(challange,m=3):
	# find one having least candidates as beginner
	least,x,y = m**2,-1,-1
	for i,j in itertools.product(range(m**2),repeat=2):
		if not challange[i][j]:
			num = len(cal_candidate(challange,i,j))
			if num < least:
				least = num
				x,y = i,j
	return x,y

def try_candidate(challange,id,m=3):
	# ending..
	if is_full(challange):
		return challange

	# (x,y) apart from id
	x = id / (m**2)
	y = id % (m**2)	
	
	# judge whether current is null or not
	# find a null one
	# +1 => first in row,then in column
	while challange[x][y]:
		id =  (id +1)%m**4
		x = id/(m**2)
		y = id%(m**2)
	candidate = cal_candidate(challange,x,y)

	# error or not
	if len(candidate) == 0:
		return False

	# recusion
	for i in range(len(candidate)):
		challange[x][y] = candidate[i]
		# next one
		result_r = try_candidate(challange,(id+1)%m**4)
		if not result_r:
			# if next one == None, return False
			# we try another one
			pass
		else:
			# if next one == OK
			# we return OK
			return challange
	# all candidates are not suitable,we return ERROR
	else:
		# Must return to what we are like before
		challange[x][y] = None
		return False

def solving_sudoku(challange,m=3):
	# judge whether is full
	if is_full(challange):
		return challange

	# prepare for recusion --- find beginner
	x,y = least_candidate(challange)

	# to be convient, we use id to represent location
	id = x *(m**2) + y

	# try_candidate is our recusion function
	result = try_candidate(challange,id)
	return result

if __name__ == "__main__":
	Board = make_board()
	challange = print_board(Board)
	wait = raw_input("PRESS ENTER TO SHOW THE ANSWER.")
	print('Raw Answer: ')
	print_answers(Board)
	print('Calculated from our algorithm: ')
	result = solving_sudoku(challange)
	print_answers(result)

