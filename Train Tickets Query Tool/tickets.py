#! /usr/bin/env python3
#-*- coding:gbk -*-

"""
Train tickets query via command-line.

Usage:
	tickets [-gdtkz] <from> <to> <date>

Options:
	--h,--help	HELP
	-g		GAO
	-d		DONG
	-t		TE
	-k		KUAI
	-z		ZHI

Example:
	tickets beijing shanghai 2016-08-25
"""
from docopt import docopt	#docopt:Python3 cmd index translate tools
from stations import stations
import requests
from prettytable import PrettyTable	#prettytable:format print message like MYSQL

class TrainCollection(object):
	header = 'train station time duration first second softsleep hardsleep hardsit'.split()
	def __init__(self,rows):
		self.rows = rows
	
	def _get_duration(self,row):
		duration = row.get('lishi').replace(':','h')+'m'
		if duration.startswith("00"):
			return duration[4:]
		if duration.startswith('0'):
			return duration[1:]
		return duration

	@property
	def trains(self):
		for row in self.rows:
			train = [row['station_train_code'],
				'\n'.join([row['from_station_name'],row['to_station_name']]),
				'\n'.join([row['start_time'],row['arrive_time']]),
				self._get_duration(row),
				row['zy_num'],
				row['ze_num'],
				row['rw_num'],
				row['yw_num'],
				row['yz_num']]
			yield train

	def pretty_print(self):
		pt = PrettyTable()
		pt._set_field_names(self.header)
		for train in self.trains:
			pt.add_row(train)
		print(pt)
		#print u'\u5317\u4eac\u5357\n\u4e0a\u6d77' cmd中直接输出就是中文，但在【】中用pt输出就是乱码。。有待研究

def cli():
	"""command-line interface"""
	arguments = docopt(__doc__)
	from_station = stations.get(arguments['<from>'])
	to_station = stations.get(arguments["<to>"])
	date = arguments['<date>']
	
	url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(date, from_station, to_station)
	r = requests.get(url,verify=False)
	rows = r.json()["data"]["datas"]
	trains = TrainCollection(rows)
	trains.pretty_print()

if __name__ == "__main__":
	cli()
