#-*- coding:utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

# First Part: SGDClassifier
# prepare data
test_set = pd.read_csv('raw/TestSet.csv')
train_set = pd.read_csv('raw/TrainingSet.csv')

train = train_set.drop(['EbayID','QuantitySold','SellerName'],axis=1)
train_target = train_set['QuantitySold']

n_trainSamples,n_features = train.shape

# draw compared different mini_batch learning result
def plot_learning(clf,title):
	plt.figure()
	# record prediction of last_training_result applied on batch now
	validationScore = []
	# record prediction of now_training_result applied on batch now 
	trainScore = []
	mini_batch = 1000

	for idx in range(int(np.ceil(n_trainSamples/mini_batch))):
		x_batch = train[idx*mini_batch:min((idx+1)*mini_batch,n_trainSamples)]
		y_batch = train_target[idx*mini_batch:min((idx+1)*mini_batch,n_trainSamples)]

		if idx>0:
			validationScore.append(clf.score(x_batch,y_batch))
		clf.partial_fit(x_batch,y_batch,classes=range(5))	# add now paragrams
		if idx>0:
			trainScore.append(clf.score(x_batch,y_batch))
	
	plt.plot(trainScore,label="train score")
	plt.plot(validationScore,label="validation score")
	plt.xlabel('Mini_batch')
	plt.ylabel('Score')
	plt.legend(loc='best')
	plt.grid()
	plt.title(title)

# make data to [0,1]
scaler = StandardScaler()
train = scaler.fit_transform(train)
# create SGDClassifier
clf = SGDClassifier(penalty='l2',alpha=0.001)
plot_learning(clf,'SGDClassifier')
#plt.show()

# Second Part : decrease 
from sklearn import (manifold,decomposition,random_projection)
from matplotlib import offsetbox
from time import time

# image[0]==0 represents isSold==0
images = []
images.append([[  0. ,   0. ,   5. ,  13. ,   9. ,   1. ,   0. ,   0. ],
 [  0. ,   0. ,  13. ,  15. ,  10. ,  15. ,   5. ,   0. ],
 [  0. ,   3. ,  15. ,   2. ,   0. ,  11. ,   8. ,   0. ],
 [  0. ,   4. ,  12. ,   0. ,   0. ,   8. ,   8. ,   0. ],
 [  0. ,   5. ,   8. ,   0. ,   0. ,   9. ,   8. ,   0. ],
 [  0. ,   4. ,  11. ,   0. ,   1. ,  12. ,   7. ,   0. ],
 [  0. ,   2. ,  14. ,   5. ,  10. ,  12. ,   0. ,   0. ],
 [  0. ,   0. ,   6. ,  13. ,  10. ,   0. ,   0. ,   0. ]])
# image[1]==1 represents isSold==1
images.append([[  0. ,   0. ,   0. ,  12. ,  13. ,   5. ,   0. ,   0. ],
 [  0. ,   0. ,   0. ,  11. ,  16. ,   9. ,   0. ,   0. ],
 [  0. ,   0. ,   3. ,  15. ,  16. ,   6. ,   0. ,   0. ],
 [  0. ,   7. ,  15. ,  16. ,  16. ,   2. ,   0. ,   0. ],
 [  0. ,   0. ,   1. ,  16. ,  16. ,   3. ,   0. ,   0. ],
 [  0. ,   0. ,   1. ,  16. ,  16. ,   6. ,   0. ,   0. ],
 [  0. ,   0. ,   1. ,  16. ,  16. ,   6. ,   0. ,   0. ],
 [  0. ,   0. ,   0. ,  11. ,  16. ,  10. ,   0. ,   0. ]])

# select 1000 examples to display
show_instancees = 1000
# define the drawing function
def plot_embedding(X,title=None):
	# basic --- make to [0,1]
	x_min,x_max = np.min(X,0),np.max(X,0)
	X = (X - x_min) / (x_max - x_min)

	plt.figure()
	ax = plt.subplot(111)
	# num of records
	for i in range(X.shape[0]):
		plt.text(X[i,0],X[i,1],str(train_target[i]),color = plt.cm.Set1(train_target[i] / 2.),fontdict={'weight':'bold','size':9})
	
	if hasattr(offsetbox,'AnnotationBbox'):
		shown_images = np.array([[1.,1.]])	# just a big one
	for i in range(show_instancees):
		dist = np.sum((X[i]-shown_images)**2,1)
		if np.min(dist) < 4e-3:
			# not to show points that are too close
			continue
		shown_images = np.r_[shown_images,[X[i]]]
		auctionbox = offsetbox.AnnotationBbox(offsetbox.OffsetImage(images[train_target[i]],cmap=plt.cm.gray_r),X[i])
		ax.add_artist(auctionbox)
	plt.xticks([]),plt.yticks([])
	if title is not None:
		plt.title(title)

# Random Projection
start_time = time()
rp = random_projection.SparseRandomProjection(n_components=2,random_state=42)
rp.fit(train[:show_instancees])
train_projected = rp.transform(train[:show_instancees])
plot_embedding(train_projected,"Random Projection of the auction (time:%.3fs)"%(time()-start_time))

# PCA
start_time = time()
train_pca = decomposition.TruncatedSVD(n_components=2).fit_transform(train[:show_instancees])
plot_embedding(train_pca,"Pricincipal components projection of the auction (time:%.3fs)"%(time()-start_time))

# t-sne
start_time = time()
tsne = manifold.TSNE(n_components=2,init='pca',random_state=0)
train_tsne = tsne.fit_transform(train[:show_instancees])
plot_embedding(train_tsne,"T-SNE embedding of the auction (time:%.3fs)"%(time()-start_time))

plt.show()

# Third Part: test 
from sklearn.metrics import (precision_score,recall_score,f1_score)

# prepare data
test = test_set.drop(['EbayID','QuantitySold','SellerName'],axis=1)
test_target = test_set['QuantitySold']
test = scaler.fit_transform(test)

# predict via trained clf
test_pred = clf.predict(test)

print('SGDClassifier training performance on testing dataset:')
print('\tPrecision: %1.3f '% precision_score(test_target,test_pred))
print('\tRecall: %1.3f '% recall_score(test_target,test_pred))
print('\tF1: %1.3f \n'% f1_score(test_target,test_pred))