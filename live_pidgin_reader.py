import psycopg2
import pandas as pd
import pickle
import time
import calendar
from pydbus import SessionBus
from gi.repository import GObject
#Import custom functions
from reader_class import *

#Import prebuild models
with open('current_model','r') as file:
 	model = pickle.load(file)
with open('current_cluster_model','r') as file:
 	cluster_model = pickle.load(file)
with open('current_wv_model','r') as file:
	wv_model = pickle.load(file)

#Connect to the psql database
con = psycopg2.connect(database = 'twitch', user = 'adam', host='localhost', password='*')
cur = con.cursor()

#Determin the starting index from the psql data base
sql_query="""SELECT twitch.Index FROM twitch"""
query_result = pd.read_sql_query(sql_query,con)
index = query_result['index'].max()+1

#initilize the reader class
reader=reader(model,cluster_model,wv_model,cur,con,index)

#Create the connection to the pidgin client
bus = SessionBus()
purple = bus.get("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")

#read messages to a psql database
purple.ReceivedChatMsg.connect(reader.read)
GObject.MainLoop().run()