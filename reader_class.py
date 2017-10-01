import calendar
import time
import pandas as pd
import re
import numpy as np
#custome funtions
from Twitch_Data.preprocessingtools import string_trunc,auto_flag_string,extrace_advanced_features


def get_streamer(con):
	"""Given a list of messaages determins the streamer and return the name of the streamer"""
	search_length = 60
	start_time = str(calendar.timegm(time.gmtime())-search_length)
	#Create the list of known streamer names
	streamers=['amaz','hafu','kibler','savjz','kolento','reynad','thijs','dog']
	#Get the list of the last 60 seconds of messages from the active streamer
	sql_query = """SELECT edited_message FROM twitch WHERE %s<=time AND 1.0=active;"""%start_time
  	messages = list(pd.read_sql_query(sql_query,con)['edited_message'])
	_string = ' '.join(messages)
	_string=_string.lower()
	words = re.split('[^a-z0-9]',_string)
	#Cout the numebr of occurences where the streamers name is a substring
	counts=[0]*len(streamers)
	for i in range(0,len(streamers)):
		count = 0
		for word in words:
			if streamers[i] in word:
				count=count+1
		counts[i]=count
	#Return the streamer whose name got the most counts
	if counts == [0]*len(streamers):
		return 'unknown'
	return streamers[counts.index(max(counts))]

class reader():
	def __init__(self,model,cluster_model,wv_model,cur,con,index):
		self.model = model#The predictive model
		self.con=con#The psql connection
		self.cur = cur#the psql curson
		self.index=index#The index to start at for the psql data base
		self.game='HS'#The name of the game
		self.cluster_model=cluster_model#The model for clustering
		self.wv_model=wv_model#The word to vec model
		self.active_streamer = '0'#Intilize the active streamer variable
		self.last_refresh = calendar.timegm(time.gmtime())
		self.streamer_name='unknown'

	def set_active(self):
		"""set the active streamer variable"""
		self.last_refresh=calendar.timegm(time.gmtime())
		start_time = str(calendar.timegm(time.gmtime())-20)
		sql_query = """SELECT streamer FROM twitch WHERE %s<=time;"""%start_time
  		query_result = pd.read_sql_query(sql_query,con)
  		_list = list(query_result['streamer'])
  		streamers = list(set(_list))
  		counts = []
  		#Determins if no messages have appeared for the active streamer in 20 seconds
  		if len(_list)!=0 and not (self.active_streamer in _list):
  			self.streamer_name='unknown'
  			for streamer in streamers:
  				counts.append(_list.count(streamer))
  			self.active_streamer=streamers[counts.index(max(counts))]#Sets active streamer to the one with the fastest chat

	def read(self,account, sender, message, conversation, flags):
		"""Will live update a sql data base about incoming messages. The data base includes: the message
		a truncated message, an index, the time of the message,the sender of the message and the probality it
		is spam. inputs are IRC account, sender, message,converation, auto spam flags"""
		edited_message =string_trunc(message)#Removes unnessissary characters and makes the message lowercase
		if auto_flag_string(message)==1:#Filters out messages with no words
			prob = '0'
		else:#Extracts the features needed for the model
			model_features = extrace_advanced_features(self.wv_model,self.cluster_model,message,edited_message,'steming')
			model_features=model_features.reshape(1,-1)
			prob = self.model.predict_proba(model_features)
			prob = prob[0][1]
			prob = str(prob)
		#Labels if the message belongs to the active streamer
		if str(conversation)==self.active_streamer:
			active='1'
		else:
			active='0'
		current_time = str(calendar.timegm(time.gmtime()))
		#Transforms the output into a string for use in a psql queary
		output='(0,\''+edited_message+'\',\''+self.game+'\','+str(self.index)+',\''+sender+'\','
		output=output+current_time+',\''+str(conversation)+'\','+prob+','+active+',\''+self.streamer_name+'\')'
		#adds a row to a psql database
		cur.execute("""INSERT INTO twitch VALUES %s;"""%output)
		con.commit()
		if (self.last_refresh+60)<calendar.timegm(time.gmtime()):
			self.streamer_name=get_streamer(self.con)
			self.set_active()
		#updates the index
		self.index = self.index+1