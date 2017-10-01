import pandas as pd
import calendar
import time

def compute_from_tables(split_query_results):
  """Given a list of four tables computes ordered most to leaast recent computes the variables need for
  the output function to give the html table"""
  if not split_query_results[0].empty:
    M = list(split_query_results[0]['edited_message'])
    S = list(split_query_results[0]['sender'])
    P = list(split_query_results[0]['prob'])
    indices=sorted(range(len(M)),key=lambda x: P[x])
    results = []#Will be ordered most to least relavent
    senders = []#Will be ordered most to least relavent
    for i in indices:
      results = [M[i]]+results
      senders = [S[i]]+senders
    length = len(results)
    for i in range(length,4):
      results.append(' ')
      senders.append(' ')
    for i in range(0,4):
      if senders[i]!= ' ':
        senders[i]=str(i+1)+') '+senders[i]+': '
  else:
    results= [' ',' ',' ',' ']
    senders= [' ',' ',' ',' ']
  old_best_messages=[' ']*6
  old_best_senders=[' ']*6
  for i in range(7):
    if not split_query_results[i].empty:
      max_prob=split_query_results[i]['prob'].max()
      best_table = split_query_results[i][split_query_results[i]['prob']==max_prob]
      best_message=list(best_table['edited_message'])[0]
      best_sender=list(best_table['sender'])[0]
      old_best_messages[i-1]=best_message
      old_best_senders[i-1]=best_sender+':'
  return [results, senders,old_best_messages,old_best_senders]

def normal_output(delay,con):
  """Given the delay querys the sql data base and returns what is needed for the html output"""
  current_time=calendar.timegm(time.gmtime())
  start_time = current_time-(int(delay)*4)
  sql_query = """SELECT edited_message,prob,sender,time,streamer_name FROM twitch WHERE %s<=time AND 1.0=active;"""%start_time
  query_results = pd.read_sql_query(sql_query,con)
  streamer_name='unknown'
  if not query_results.empty:
    streamer_name = list(query_results['streamer_name'])[-1]
  split_query_results=[]
  for i in range(0,7):
    split_query_results.append(query_results[(query_results['time']>(current_time-(i+1)*int(delay))) & (query_results['time']<=(current_time-i*int(delay)))])
  return compute_from_tables(split_query_results)+['Currently live with: '+streamer_name]

def rerun_output(delay,rerun,con):
  delay = int(delay)
  current_time=calendar.timegm(time.gmtime())
  rerun_duration = current_time-rerun
  sql_query = """SELECT edited_message,prob,sender,index FROM twitch WHERE {0}>=index AND {1}<=index;""".format(rerun_duration,rerun_duration-4*delay)
  query_results = pd.read_sql_query(sql_query,con)
  split_query_results=[]
  for i in range(0,7):
    split_query_results.append(query_results[(query_results['index']>(rerun_duration-(i+1)*delay)) & (query_results['index']<=(rerun_duration-i*delay))])
  return compute_from_tables(split_query_results)+['Currently showing reruns']

def check_rerun(rerun,con):
  current_time = calendar.timegm(time.gmtime())
  start_time = current_time-60
  sql_query = """SELECT edited_message,prob,sender,time,streamer_name FROM twitch WHERE %s<=time AND 1.0=active;"""%start_time
  query_results = pd.read_sql_query(sql_query,con)
  if query_results.empty:
    if rerun=='no':
      offset= 140000
      return current_time-offset
  else:
    return 'no'