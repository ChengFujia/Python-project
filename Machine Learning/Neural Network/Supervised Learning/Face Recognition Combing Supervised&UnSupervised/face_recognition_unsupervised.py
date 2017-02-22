import scipy.io as scio
import numpy as np
import matplotlib.pyplot as plt
import random

# 利用自编码器实现特征提取和数据降维
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
	# using z-score -- HGIHLINE
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









