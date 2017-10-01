from flask import render_template
import pandas as pd
from flask import request
from flaskexample import app
import pickle
import time
import calendar
import psycopg2
#custom packages
from Final_Product_Tools import *

global results
results =[' ']*8
global senders
senders =[' ']*8
global con
con = psycopg2.connect(database = 'twitch', user = 'adam', host='localhost', password='b2ak11')

@app.route('/')
@app.route('/index')
# def index():
#     return render_template("index.html",
#        title = 'Home', user = { 'nickname': 'Miguel' },
#        )

@app.route('/input')
def input():
    return render_template("input.html")

@app.route('/about')
def about():
  return render_template("about.html")

@app.route('/output')
def output():
  delay = request.args.get('delay')
  start_time = calendar.timegm(time.gmtime())-int(delay)
  sql_query = """SELECT message,prob,sender FROM twitch WHERE %s<=time AND 1.0=active;"""%start_time
  query_result = pd.read_sql_query(sql_query,con)
  if not query_result.empty:
    max_prob=query_result['prob'].max()
    query_result=query_result[query_result['prob']==max_prob]
    result_string=list(query_result['message'])[0]
    sender_string=list(query_result['sender'])[0]
    global results
    results.append(result_string)
    del results[0]
    global senders
    senders.append(sender_string+':')
    del senders[0]
  else:
    result_string=''
    sender_string=''
  return render_template("simpleoutput.html", result1 = results[-1],result2=results[-2],result3=results[-3],
    result4=results[-4],result5=results[-5],result6=results[-6],
    sender1 = senders[-1],sender2=senders[-2],sender3=senders[-3],
    sender4=senders[-4],sender5=senders[-5],sender6=senders[-6],delay=delay)
