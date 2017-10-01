from __future__ import division

import pandas as pd
import numpy as np
import re
import enchant
from collections import Counter
import pickle
import psycopg2
from nltk.stem.snowball import SnowballStemmer

def string_trunc(string):
	"""removes all characters from a string expect englisht letters aand .,!?@<>()\- and set all letters to lowercase"""
	regex = re.compile('[^a-zA-Z0-9.,!?@ <>()\-]')
	return regex.sub('', string.lower())

#Removes unessissaary symboles and capilitizations
def message_trunc(df):
	"""accepts as input a data frame with a message column of strings. returns the data frame with a new column
	names edited message which is the messaage colum with the string_trunc function appled to it"""
	df['edited message']=df['message'].apply(string_trunc)
	return df

def single_letter(word):
	"""Takes as input a string and returns true if the string is one letter that is no a or I and false otherwise"""
	if len(word)==1 and word!='a' and word!='I':
		return True
	return False

def number_of_word(string,d):
	"""Given a string and a spell check (denoted by d) returns the number of words delimated by no english characters"""
	words = re.split('[^a-z]',string)
	words = filter(lambda x: x != '', words)
	number = 0
	if words == []:
		return 0
	for word in words:
		if d.check(word) and not single_letter(word):
			number = number +1
	return number

def number_of_words_in_list(string,_list):
	"""Given a string and a list returns the number of words in the string that are in the list where words are
	seperated by non-english characters"""
	words = re.split('[^a-z]',string)
	words = filter(lambda x: x != '', words)
	number = 0
	if words == []:
		return 0
	for word in words:
		if word in _list:
			number = number +1
	return number

def caps_ratio(string):
	"""Given a string gives the ration (capital english letters)/total english letters. Returning 0 is no english
	letters are present"""
	regex = re.compile('[^A-Z]')
	caps=regex.sub('', string)
	regex = re.compile('[^a-z]')
	total=regex.sub('', string.lower())
	if len(total) ==0:
		return 0
	return len(caps)/len(total)

def symbole_density(string):
	"""Takes as input a string and returns the nuber of non english characters over the total length of the
	string, returns 0 if it is an empty string"""
	size = len(string)
	regex = re.compile('[a-z ]')
	symbole_size=len(regex.sub('', string.lower()))
	if size == 0:
		return 0
	return symbole_size/size

def super_edited_message(string,twitchword_list):
	"""Take as input a string and a list of words and returns the string with thoughs words removed
	when non alpha numeric characters are treated as spaces for determining words"""
	words = re.split('[^a-z0-9]',string)
	words = filter(lambda x: x != '', words)
	new_words=[]
	for word in words:
		if not word in twitchword_list:
			new_words.append(word)
	return ' '.join(new_words)

def shrink_fearutes(n,X,importance):
	"""Truncates X to include only the most important n fetures"""
	indices = sorted(range(100),key=lambda x:importance[x])[-n:]
	X_words=X[:100]
	X_tail=X[100:]
	new_words=[]
	for i in indices:
		new_words.append(X[i])
	return list(new_words)+list(X_tail)

def auto_flag_string(string):
	"""Returns 1 if the string contains no english or hearthstone words otherwise returns 0"""
	with open('hsword_list','r') as file:
		hsword_list=pickle.load(file)
	if number_of_word(string,enchant.Dict("en_US"))==0 and number_of_words_in_list(string,hsword_list)==0:
		return 1
	else:
		return 0

#Connects to a psql database
con = psycopg2.connect(database = 'twitch', user = 'adam', host='localhost', password='*')
cur=con.cursor()

#Creates a stemmer object
snowball = SnowballStemmer('english')

#Stemms a list and returns it
def english_stemmer(_list):
    for i in range(0,len(_list)):
        _list[i]=snowball.stem(_list[i])
    return _list

def get_sentences(*arg):
	"""Get back list of words of each message in the database twitch and table twitch stems them if any argument is passed"""
	sql_query ="""
	SELECT edited_message FROM twitch;
	"""
	messages = pd.read_sql_query(sql_query,con)
	messages['edited_message']=messages['edited_message'].apply(lambda x:re.split('[^a-z0-9]',x.lower()))
	if len(arg)!=0:
		messages['edited_message']=messages['edited_message'].apply(english_stemmer)
	sentences = list(messages['edited_message'])
	return sentences

def question_mark_at_end(message):
	if message[-1]=='?':
		return 1
	else:
		return 0

def number_of_spaced_words(message):
	"""given a string returns the number of space delimiated words"""
	words = message.split(' ')
	return len(words)

def extrace_advanced_features(word_vec,cluster_model,message,edited_message,*arg):
	"""Exactrs features as follows [...word clusters...,does it end in a question mark,caps ratio,symbol densinity, message length]"""
	number_of_clusters = len(cluster_model.cluster_centers_)
	vocab = word_vec.wv.vocab
	features = [0]*(number_of_clusters)
	words = re.split('[^a-z0-9]',edited_message.lower())
	words = filter(lambda x: x != '', words)
	if len(arg)!=0:
		words = english_stemmer(words)
	for word in words:
		if word in vocab:
			cluster_number = cluster_model.predict(np.array(word_vec.wv[word]).reshape(1,-1))[0]
			features[cluster_number]=features[cluster_number]+1
	features.append(number_of_spaced_words(edited_message))
	features.append(caps_ratio(message))
	features.append(symbole_density(message))
	features.append(len(message))
	return np.array(features)