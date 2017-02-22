from __future__ import division
import scipy.io as scio
import numpy as np
import matplotlib.pyplot as plt
import random

# feedforward computing
def feedforward(w,a,x):
	# sigmoid function
	f = lambda s: 1/(1+np.exp(-s))

	w = np.array(w)
	temp = np.array(np.concatenate((a,x),axis=0))
	z_next = np.dot(w,temp)

	return f(z_next),z_next

# delta backprop
def backprop(w,z,delta_next):
	# sigmoid function
	f = lambda s: 1/(1+np.exp(-s))
	df = lambda s:f(s) * (1-f(s))
	delta = df(z) * np.dot(w.T,delta_next)
	
	return delta

# import face images
DataSet = scio.loadmat('yaleB_face_dataset.mat')
unlabeledData = DataSet['unlabeled_data']

dataset_size = 80 #20/each * 4 iamges
unlabeled_data = np.zeros(unlabeledData.shape)

for i in range(dataset_size):
	# gray 
	tmp = unlabeledData[:,i] / 255.
	# using z-score -- HGIHLIGHT
	unlabeled_data[:,i] = (tmp-np.mean(tmp)) / np.std(tmp)

# set autoencoder training paragrams
alpha = 0.5 
max_epoch = 300
mini_batch = 10
height = 48
width = 42
imgSize = height * width

# nerve net structure
hidden_node = 60
hidden_layer = 2
layer_struc = [[imgSize,1],
		[0,hidden_node],
		[0,imgSize]]
layer_num = 3

# initinial weight -- w
w = []
for l in range(layer_num-1):
	w.append(np.random.randn(layer_struc[l+1][1],sum(layer_struc[l])))

# define nerve net outer nodes
X = []
X.append(np.array(unlabeled_data[:,:]))
X.append(np.zeros((0,dataset_size)))
X.append(np.zeros((0,dataset_size)))

# define init--delta delta
delta = []
for l in range(layer_num):
	delta.append([])

# First : output original images in first line
# define result display format
nRow = max_epoch / 100 + 1
nColumn = 4
eachFaceNum = 20

# first line
for iImg in range(nColumn):
	ax = plt.subplot(nRow,nColumn,iImg+1)
	#1-20(b01) 21-40(b02) 41-60(b03) 61-80(b04)
	#1 , 21, 41, 61
	plt.imshow(unlabeledData[:,eachFaceNum * iImg+1].reshape((width,height)).T,cmap=plt.cm.gray)
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)

# unsupervised training
count = 0
print('Autoencoder training start...')
for iter in range(max_epoch):
	# define shuffle
	ind = list(range(dataset_size))
	random.shuffle(ind)

	a = []
	z = []
	z.append([])
	for i in range(int(np.ceil(dataset_size / mini_batch))):
		a.append(np.zeros((layer_struc[0][1],mini_batch)))
		x = []
		for l in range(layer_num):
			x.append(X[l][:,ind[i*mini_batch : min((i+1)*mini_batch,dataset_size)]])
		y = unlabeled_data[:,ind[i*mini_batch : min((i+1)*mini_batch,dataset_size)]]
		for l in range(layer_num -1):
			a.append([])
			z.append([])
			a[l+1],z[l+1] = feedforward(w[l],a[l],x[l])

		delta[layer_num-1] = np.array(a[layer_num-1]-y) * np.array(1-a[layer_num-1])
		delta[layer_num-1] = delta[layer_num-1] * np.array(1-a[layer_num-1])

		for l in range(layer_num-2,0,-1):
			delta[l] = backprop(w[l],z[l],delta[l+1])
		for l in range(layer_num-1):
			dw = np.dot(delta[l+1],np.concatenate((a[l],x[l]),axis=0).T) / mini_batch
			w[l] = w[l] - alpha * dw
	count = count + 1

	# every 100 times show mid-result
	if np.mod(iter+1,100) == 0:
		b = []
		b.append(np.zeros((layer_struc[0][1],dataset_size)))
		
		for l in range(layer_num-1):
			tempA,tempZ = feedforward(w[l],b[l],X[l])
			b.append(tempA)

		for iImg in range(nColumn):
			ax = plt.subplot(nRow,nColumn,iImg + nColumn*(iter+1)/100 +1)
			tmp = b[layer_num-1][:,eachFaceNum * iImg + 1]
            		dis_result = ((tmp * np.std(tmp)) + np.mean(tmp)).reshape(width,height).T
            		plt.imshow(dis_result,cmap= plt.cm.gray) 
            		ax.get_xaxis().set_visible(False)
            		ax.get_yaxis().set_visible(False)
		print('Learning epoch:',count,'/',max_epoch)
"""
# compare original img with encoded img
fig2 = plt.figure(2)
code_result, tempZ = feedforward(w[0], b[0], X[0])

# show original img
for iImg in range(nColumn):
    ax = plt.subplot(2, nColumn, iImg+1)
    plt.imshow(unlabeled_data[:,eachFaceNum * iImg + 1].reshape((width,height)).T, cmap= plt.cm.gray)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

# show encoded img
for iImg in range(nColumn):
    ax = plt.subplot(2,nColumn,iImg+nColumn+1)
    plt.imshow(code_result[:,eachFaceNum * iImg + 1].reshape((hidden_node,1)), cmap=plt.cm.gray)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

plt.show()
"""

# define supervised learning paragrams
supervised_alpha = 0.5
max_epoch = 200
mini_batch = 14
SJ = []		#bias value 
SAcc = []	#right or error rate

# initinal supervised learning net structure
SL_layer_struc = []
SL_layer_num = 2
SL_layer_struc = [[0,hidden_node],
		[0,4]]

# initinal supervised_weight
supervised_weight = []
for l in range(SL_layer_num-1):
	supervised_weight.append(np.random.randn(SL_layer_struc[l+1][1],sum(SL_layer_struc[l])))

# supervised learning delta
delta = []
for l in range(SL_layer_num):
	delta.append([])

# load training data
trainData = DataSet['trainData']
trainData = trainData[:,:]
train_data = np.zeros(trainData.shape)

# make to 0-1
trainData_size = 56
for i in range(trainData_size):
	tmp = trainData[:,i]
	# using z-zone 
	train_data[:,i] = (tmp-np.mean(tmp)) / np.std(tmp)
# compared with unsupervised training -- add those labels
train_labels = DataSet['train_labels']
train_labels = train_labels[:,:]

# load test data
testData = DataSet['testData']
testData = testData[:,:]
test_data = np.zeros(testData.shape)

# make to 0-1
testData_size = 40
for i in range(testData_size):
	tmp = testData[:,i]
	test_data[:,i] = (tmp-np.mean(tmp))/np.std(tmp)

test_labels = DataSet['test_labels']
test_labels = test_labels[:,:]

# using autoencoder get trainData_set&testData_set's code
# trainSet 
a = []
a.append(np.zeros((layer_struc[0][1],trainData_size)))
for l in range(hidden_layer-1):
	if l==0:
		tmpA,tmpZ = feedforward(w[l],a[l],train_data)
		a.append(tmpA)
	else:
		tmpA,tmpZ = feedforward(w[l],a[l],np.zeros((0,trainData_size)))
		a.append(tmpA)
small_trainData = a[hidden_layer-1]

# testSet
a = []
a.append(np.zeros((layer_struc[0][1],testData_size)))
for l in range(hidden_layer-1):
	if l==0:
		tmpA,tmpZ = feedforward(w[l],a[l],test_data)
		a.append(tmpA)
	else:
		tmpA,tmpZ = feedforward(w[l],a[l],np.zeros((0,testData_size)))
		a.append(tmpA)
small_testData = a[hidden_layer-1]

# supervised learning
def supervised_training():
	global SJ
	global SAcc
	
	print('Supervised training start...')
	for iter in range(max_epoch):
		# shuffle the data
		ind = list(range(trainData_size))
		random.shuffle(ind)

		a = []
		z = []
		z.append([])
		# batch one by one training -- confirm each one be trained
		for i in range(int(np.ceil(trainData_size / mini_batch))):
			# net inner node
			a.append(small_trainData[:,ind[i*mini_batch:min((i+1)*mini_batch,trainData_size)]])
			# prepare outer node
			x = []
			for l in range(SL_layer_num):
				x.append(np.zeros((0,min((i+1)*mini_batch,trainData_size)-i*mini_batch)))
			# target output
			y = train_labels[:,ind[i*mini_batch:min((i+1)*mini_batch,trainData_size)]]

			# feedforward computing
			for l in range(SL_layer_num-1):
				a.append([])
				z.append([])
				a[l+1],z[l+1] = feedforward(supervised_weight[l],a[l],x[l])
			
			# delta computing
			delta[SL_layer_num-1] = np.array(a[SL_layer_num-1]-y)*np.array(a[SL_layer_num-1])
			delta[SL_layer_num-1] = delta[SL_layer_num-1] * np.array(1-a[SL_layer_num-1])

			# delta d-direction
			for l in range(SL_layer_num-2,0,-1):
				delta[l] = backprop(supervised_weight[l],z[l],delta[l+1])

			for l in range(SL_layer_num-1):
				dw = np.dot(delta[l+1],np.concatenate((a[l],x[l]),axis=0).T) / mini_batch
				supervised_weight[l] = supervised_weight[l] - supervised_alpha * dw
			
			# make necessary computings
			tmpResult = a[SL_layer_num-1]
			SJ.append(np.sum(np.multiply(tmpResult[:]-y[:],tmpResult[:]-y[:]))/2/mini_batch)
			SAcc.append(float(sum(np.argmax(y,axis=0)==np.argmax(tmpResult,axis=0))/mini_batch))
	
	# show changes during training process
	print('Supervised learning done!')
	plt.figure()
	plt.plot(SJ)
	plt.title('loss function')
	plt.figure()
	plt.plot(SAcc)
	plt.title('Accuracy')

def supervised_testing():
	print('Testing...')
	
	# train_set accuracy
	tmpA,tmpZ = feedforward(supervised_weight[0],small_trainData,np.zeros((0,trainData_size)))
	train_pred = np.argmax(tmpA,axis=0)
	train_res = np.argmax(train_labels,axis=0)
	train_acc = float(sum(train_pred==train_res)/trainData_size) * 100
	print('Training accuracy:%.2f%c'%(train_acc,'%'))

	# test_set accuracy
	tmpA,tmpZ = feedforward(supervised_weight[0],small_testData,np.zeros((0,testData_size)))
	test_pred = np.argmax(tmpA,axis=0)
	test_res = np.argmax(test_labels,axis=0)
	test_acc = float(sum(test_pred==test_res)/testData_size) * 100
	print('Testing accuracy:%.2f%c'%(test_acc,'%'))

supervised_training()
supervised_testing()

plt.show()