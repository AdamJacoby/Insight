#from Final_Product_T
import numpy as np
from math import floor
import random

def Train_Accucary(model,X,Y,splitter):
	"""Given a model X,Y and a splitter computed the mean training error on the splits"""
	mean=0
	count =0
	for test_index,ignore in splitter:
		X_train=[]
		Y_train=[]
		for i in test_index:
			X_train.append(X[i])
			Y_train.append(Y[i])
		mean=mean+model.fit(X_train,Y_train).score(X_train,Y_train)
		count = count+1
	return mean/count

def get_prob_from_list(Y):
	"""Given an ordered list of 1s and 0s compute the chance a randomly selected 1 is higher then a randomly selected
	0"""
	total_1 = Y.count(1)
	total_0=Y.count(0)
	total_prob=0
	for i in range(0,len(Y)):
		if Y[i]==1:
			below = Y[i:].count(0)
			prob=below/float(total_0)
			total_prob=total_prob+prob
	return total_prob/float(total_1)

def pre_tga(trained_model,X_test,Y_test,test_flag):
	temp_prob = list(trained_model.predict_proba(X_test))
	test_prob0=[]
	test_prob1=[]
	for i in temp_prob:
		test_prob0.append(i[0])

	for i in range(0,len(test_flag)):
		if test_flag==1:
			test_prob[i]==0
	indices0 = sorted(range(len(X_test)),key=lambda x:test_prob0[x])
	ordered_Y_test0=[]
	for i in indices0:
		ordered_Y_test0.append(Y_test[i])
	return get_prob_from_list(ordered_Y_test0)

def top_guess_accucary(splitter,model,X,Y,auto_flag):
	acc_sum=0
	count =0
	for train_index,test_index in splitter:
		X_train=[]
		Y_train=[]
		X_test=[]
		Y_test=[]
		test_flag=[]
		for i in train_index:
			X_train.append(X[i])
			Y_train.append(Y[i])
		for i in test_index:
			X_test.append(X[i])
			Y_test.append(Y[i])
			test_flag.append(auto_flag[i])
		trained_model=model
		trained_model.fit(X_train,Y_train)
		acc_sum = acc_sum+pre_tga(trained_model,X_test,Y_test,test_flag)
		count=count+1
	return acc_sum/count
