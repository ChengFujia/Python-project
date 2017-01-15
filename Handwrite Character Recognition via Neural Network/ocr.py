def _rand_initialize_weights(self,size_in,size_out):
	#(-0.06,0.06)
	return [((x*0.12)-0.06) for x in np.random.rand(size_out,size_in)]

self.theta1 = self._rand_initialize_weights(400,num_hidden_nodes)
self.theta2 = self._rand_initialize_weights(num_hidden_nodes,10)
self.input_layer_bias = self._rand_initialize_weights(1,num_hidden_nodes)
self.hidden_layer_bias = self._rand_initialize_weights(1,10)

# inspire function -> (0,1)
def _sigmoid_scalar(self,z):
	return 1/(1+math.e**-z)

# vectorize..
self.sigmoid = np.vectorize(self._sigmoid_scalar)

# feedforward
y1 = np.dot(np.mat(self.theta1),np.mat(data['y0']).T)
sum1 = y1 + np.mat(self.input_layer_bias)
y1 = self.sigmoid(sum1)

y2 = np.dot(np.array(self.theta2),y1)
y2 = np.add(y2,self.hidden_layer_bias)
y2 = self.sigmoid(y2)

# sigmoid_prime = 1.sigmoid  2.f'(x)
actual_vals = [0] * 10
actual_vals[data['label']] = 1
output_errors = np.mat(actual_vals).T - np.mat(y2)
hidden_errors = np.multiply(np.dot(np.mat(self.theta2).T,output_errors),self.sigmoid_prime(sum1))

# change value of theta1/2 and bias1/2
self.theta1 += self.LEARNING_RATE * np.dot(np.mat(hidden_errors),np.mat(data['y0']))
self.theta2 += self.LEARNING_RATE * np.dot(np.mat(output_errors),np.mat(y1).T)
self.hidden_layer_bias += self.LEARNING_RATE * output_errors
self.input_layer_bias += self.LEARNING_RATE * hidden_errors

# equal to feedforward
def predict(self,test):
	y1 = np.dot(np.mat(self.theta1),np.mat(test).T)
	sum1 = y1 + np.mat(self.input_layer_bias)
	y1 = self.sigmoid(sum1)

	y2 = np.dot(np.array(self.theta2),y1)
	y2 = np.add(y2,self.hidden_layer_bias)
	y2 = self.sigmoid(y2)

	results = y2.T.tolist()[0]
	return results.index(max(results))


