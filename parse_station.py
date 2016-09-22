import re
import requests		#requests:Python to visit HTTP resource
from pprint import pprint#pretty print

url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8955'
r = requests.get(url,verify=False)
stations = re.findall(r'([A-Z]+)\|([a-z]+)',r.text)
stations = dict(stations)
stations = dict(zip(stations.values(),stations.keys()))
pprint(stations,indent=4)

'''HELP:run like ->python parse_station.py > stations.py
AND then add " stations = " at the begin od stations.py'''
