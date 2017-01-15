# -*- coding: UTF-8 -*-
import BaseHTTPServer
import json
from ocr import OCRNeuralNetwork
import numpy as np
import random

# server config
HOST_NAME = "localhost"
POST_NUMBER = 4000
# this value is selected by script_test
HIDDEN_NODE_COUNT = 15

# load data set
data_matrix = np.loadtxt(open('data.csv','rb'),delimiter = ',')
data_labels = np.loadtxt(open('dataLabels.csv','rb'))

# transfer to list(type)
data_matrix = data_matrix.tolist()
data_labels = data_labels.tolist()

# there are 5000 items in total. train_indice used for numbering those data
train_indice = range(5000)
random.shuffle(train_indice)

nn = OCRNeuralNetwork(HIDDEN_NODE_COUNT,data_matrix,data_labels,train_indice);

class JSONHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	# react to post(request)
	def do_GET(self):
		response_code = 200
        	response = ""
        	var_len = int(self.headers.get('Content-Length'))
        	content = self.rfile.read(var_len);
        	payload = json.loads(content);

		# if receive "train", train + save
		if payload.get('train'):
			nn.train(payload['trainArray'])
			nn.save()

		# if receive "predict", predict
		elif payload.get('predict'):
			try:
				print nn.predict(data_matrix[0])
				response = {'type':'test','result':str(nn.predict(payload['image']))}
			except:
				response_code = 500
		else:
			response_code = 400
	
		self.send_response(response_code)
		self.send_header("Content-type","application/json")
		self.send_header("Access-Control-Allow-Origin",'*')
		self.end_headers()
		if response:
			self.wfile.write(json.dump(response))
		return 

if __name__ == "__main__":
	server_class = BaseHTTPServer.HTTPServer;
	httpd = server_class((HOST_NAME,POST_NUMBER),JSONHandler)
	
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	else:
		print "Unexcepted server exception occurred."
	finally:
		httpd.server_close()

