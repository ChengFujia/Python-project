#-*- coding:utf-8 -*-
import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 利用scikit-learn中提供的诸多算法/模型实现ebay数据分析
# prepare data
test_set = pd.read_csv('raw/TestSet.csv')
train_set = pd.read_csv('raw/TrainingSet.csv')
test_subset = pd.read_csv('raw/TestSubset.csv')
train_subset = pd.read_csv('raw/TrainingSubset.csv')

#train_set.info()	# display data-vector structure 
#print(train_set[:3])	# dispaly first 3 items
train = train_set.drop(['EbayID','QuantitySold','SellerName'],axis=1)	# these 3 columns have no influence in our learning
train_target = train_set['QuantitySold']
_,n_features = train.shape	# get total number of columns

# isSold: success--1 fail--0
df = DataFrame(np.hstack((train,train_target[:,None])),columns=range(n_features)+['isSold'])
# it's not easy to distinct from columns[2,3,4,10,13],so we draw another heatmap
_ = sns.pairplot(df[:50],vars=[2,3,4,10,13],hue='isSold',size=1.5)

plt.figure(figsize=(10,10))
# compute data connections --> [[],[]]
corr = df.corr()

# make a half mask 
# get rid of half of corr as it's symmetry
mask = np.zeros_like(corr,dtype=np.bool)
mask[np.triu_indices_from(mask)] = True

# define color change
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# draw heatmap via seaborn
sns.heatmap(corr, mask=mask, cmap=cmap, vmax = .3,
                square=True, xticklabels=5, yticklabels=2,
                linewidths=.5, cbar_kws={"shrink":.5})

# want a rotate!but actually not..why?
plt.yticks(rotation=0)

plt.show()

