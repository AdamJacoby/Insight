import re
import enchant
from collections import Counter


#Removes unessissaary symboles and capilitizations
def message_trunc(string):
	regex = re.compile('[^a-zA-Z0-9.,!?@ <>()\-]')
	string = regex.sub('', string.lower())
	return string

def single_letter(word):
	if len(word)==1 and word!='a':
		return True
	return False

#counts how many words contained in a string
def number_of_word(string,d):
	words = re.split('[^a-z]',string)
	words = filter(lambda x: x != '', words)
	number = 0
	if words == []:
		return False
	for word in words:
		if d.check(word) and not single_letter(word):
			number = number +1
	return number

def number_of_words_in_list(string,_list):
	words = re.split('[^a-z]',string)
	words = filter(lambda x: x != '', words)
	number = 0
	if words == []:
		return False
	for word in words:
		if word in _list:
			number = number +1
	return number

def caps_ratio(string):
	regex = re.compile('[^A-Z]')
	caps=regex.sub('', string)
	regex = re.compile('[^a-z]')
	total=regex.sub('', string.lower())
	if len(total) ==0:
		return 0
	return len(caps)/float(len(total))

def symbole_density(string):
	size = len(string)
	regex = re.compile('[a-z ]')
	symbole_size=len(regex.sub('', string.lower()))
	if size == 0:
		return 0
	return symbole_size/float(size)


def extract_features(string):
	#['caps ratio','message length','number of hs words','number of twitch words','number of words','symbole density']
	d = enchant.Dict("en_US")
	trunc_string = message_trunc(string)
	with open('hsword_list','r') as file:
		hsword_list=pickle.load(file)
	with open('twitchword_list','r') as file:
		twitchword_list=pickle.load(file)
	return [caps_ratio(string),len(trunc_string),number_of_words_in_list(trunc_string,hsword_list),
	number_of_words_in_list(trunc_string,twitchword_list),number_of_words(trunc_string,d),
	symbole_density(string)]