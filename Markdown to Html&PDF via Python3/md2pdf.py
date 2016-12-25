"""md2pdf

translates markdown file into html or pdf,and support picture insertion .

Usage:
	md2pdf <sourcefile> <outputfile> [options]

Options:
	-h --help	show help document.
	-v --version	show version information.
	-o --output	translate sourcefile into html file.
	-p --print	translate sourcefile into pdf file and html file respectively.
	-P --Print	translate sourcefile into pdf file only.
"""

import os,re
import sys,getopt
from enum import Enum
from subprocess import call
from functools import reduce
from docopt import docopt
__version__ =  '1.0'

# parse function -- core

# define 3 enum
# define table 
class TABLE(Enum):
	Init = 1
	Format = 2
	Table = 3

# define order_list
class ORDERLIST(Enum):
	Init = 1
	List = 2

# define block
class BLOCK(Enum):
	Init = 1
	Block = 2
	CodeBlock = 3

# define whole scope -- init
table_state = TABLE.Init
orderList_state = ORDERLIST.Init
block_state = BLOCK.Init
is_code = False
is_normal = True

temp_table_first_line = []
temp_table_first_line_str = ""

need_mathjax = False

def parse(input):
	global block_state,is_normal
	is_normal = True
	result = input
	
	# check current status
	result = test_state(input)

	if block_state == BLOCK.Block:
		return result

	# analyse heading mark
	title_rank = 0
	for i range(6,0,-1):
		if input[:i] == "#"*i:
			title_rank = i
			break
	if title_rank != 0:
		result = handleTitle(input,title_rank)
		return result

	# analyse ---
	if len(input) > 2 and all_same(input[:-1],'-') and input[-1] == '\n':
		result = "<hr>"
		return result

	# analyse unordered list
	unorderd = ['+','-']
	if result !="" and result[0] in unorderd :
		result = handleUnorderd(result)
		is_normal = False

	f = input[0]
	count = 0
	sys_q = False
	while f=='>':
		count +=1
		f = input[count]
		sys_q = True
	if sys_q:
		result = "<blockquote style=\"color:#8fbc8f\"> "*count + "<b>" + input[count:] + "</b>" + "</blockquote>"*count
		is_normal = False

	# handle strange marks
	result = tokenHandler(result)
	# END

	# analysis pic link
	result = link_image(result)
	pa = re.compile(r'^(\s)*$')
	a = pa.match(input)
	if input[-1] == '\n' and is_normal==True and not a:
		result += "</br>"

	return result

def run(source_file,dest_file,dest_pdf_file,only_pdf):
	file_name = source_file
	dest_name = dest_file
	dest_pdf_name = dest_pdf_file

	# get filename's end
	_,suffix = os.path.splitext(file_name)
	if suffix not in [".md",'.markdown','.mdown','.mkd']:
		print('Error: the file should be in markdown format.')
		sys.exit(1)

	if only_pdf:
		dest_name = ".~temp~.html"

	f = open(file_name,'r')
	f_r = open(dest_name,'w')

	# first add some html attributes
	f_r.write("""<style type="text/css">div {display: block;font-family: "Times New Roman",Georgia,Serif}\
            #wrapper { width: 100%;height:100%; margin: 0; padding: 0;}#left { float:left; \
            width: 10%;  height: 100%;  }#second {   float:left;   width: 80%;height: 100%;   \
            }#right {float:left;  width: 10%;  height: 100%; \
            }</style><div id="wrapper"> <div id="left"></div><div id="second">""")
    	f_r.write("""<meta charset="utf-8"/>""")

	# parse line by line
	for eachline in f:
		result = parse(eachline)
		if result != "":
			f_r.write(result)

	
	f_r.write("""</br></br></div><div id="right"></div></div>""")

   	 # support mathjax
    	global need_mathjax
    	if need_mathjax:
        	f_r.write("""<script type="text/x-mathjax-config">\
        	MathJax.Hub.Config({tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}});\
        	</script><script type="text/javascript" \
        	src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>""")
	
	# must close
	f_r.close()
	f.close()

	if dest_pdf_name != "" or only_pdf:
		call(['wkhtmltopdf',dest_name,dest_pdf_name])	
	if only_pdf:
		call(["rm",dest_name])

# main function
def main():
	# define html file name
	dest_file = "translation_result.html"
	# define pdf file name
	dest_pdf_file = "translation_result.pdf"
	# only_pdf
	only_pdf = False

	args = docopt(__doc__,version=__version__)
	dest_file = args['<outputfile>'] if args['--output'] else dest_file
	dest_pdf_file = args['<outputfile>'] if args['--print'] or args['--Print'] else ""
	# parse
 	run(args['<sourcefile>'],dest_file,dest_pdf_file,args['--Print'])

if __name__ == '__main__':
	main()













	
