from flask import render_template
import pandas as pd
from flask import request
from flaskexample import app
import time
import calendar
import psycopg2
#custom modules
from View_Funcs import *

#Intilize Global variabls
global con
con = psycopg2.connect(database = 'twitch', user = 'adam', host='localhost', password='*')
global rerun#A flag to check if new messages are being recieves
rerun = 'no'#By defult the webpage assumes new messages will be incoming
global last_rerun_check#Counter on how long it has been since the program has last checked if new messages are coming ing
last_rerun_check=0#By defult assume it has never been checked if new reruns are incoming

#Create the website
@app.route('/')
def output():
  """returns the main web page for users"""
  delay = request.args.get('delay')#Get how often the page refreshed in seconds from user input
  try:
    delay = int(delay)
  except:
    delay=10#If user has input somthing other then an int defult the refresh rate to 10 seconds
  if delay<3:#Don't let the user reset the refresh rate to so fast that it is imposible o change in that time
    delay=3
  current_time = calendar.timegm(time.gmtime())
  global rerun
  if rerun == 'no':
    #Get the needed message from a psql database
    [results, senders,old_best_messages,old_best_senders,streamer_name]=normal_output(delay,con)
  else:
    #Get the needed message from a psql database
    [results, senders,old_best_messages,old_best_senders,streamer_name]=rerun_output(delay,rerun,con)
  global last_rerun_check
  if last_rerun_check+60<current_time:
    last_rerun_check = current_time
    rerun = check_rerun(rerun,con)#Check if new messages are no longer coming in and if so change to rerun mode
  return render_template("complexoutput.html", result1 = results[0],result2=results[1],result3=results[2],
    result4=results[3],sender1 = senders[0],sender2=senders[1],sender3=senders[2],sender4=senders[3],
    oldresult1=old_best_messages[0],oldresult2=old_best_messages[1],oldresult3=old_best_messages[2],
    oldresult4=old_best_messages[3],oldresult5=old_best_messages[4],oldresult6=old_best_messages[5],
    oldsender1=old_best_senders[0],oldsender2=old_best_senders[1],oldsender3=old_best_senders[2],
    oldsender4=old_best_senders[3],oldsender5=old_best_senders[4],oldsender6=old_best_senders[5],
    streamer_name=streamer_name,delay=delay)#return the requested results