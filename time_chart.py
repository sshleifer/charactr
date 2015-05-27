#Prepares a DF to be read in for making a timeseries chart,
#where each line is a contact, the x axis is time,
#and the y axis is characters exchanged
#Will eventually be called by chat_to_csv

import numpy as np
import pandas as pd

def getSumStats(gb):
  '''Number of characters sent and received by each group.'''
  sums = gb.agg(np.sum)
  ret = pd.DataFrame(sums.msg_len)
  ret['lensent'] = sums.snt_chars
  ret['lenrec'] = sums.msg_len - sums.snt_chars
  return ret.reset_index()

def byHour(df, hidegroups=True):
  '''accepts msg dataframe (returned by  chat_to_csv.writeChat()) 
  and groups by hour.'''
  msg = df.copy()
  if hidegroups: 
    msg = msg[msg.cname.str.startswith('chat') != True]
  msg['hour'] = msg.date.apply(lambda x : int(x[-8:-6]))
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  msg_groups = msg.groupby('hour')
  return getSumStats(msg_groups)
  
#msg.date.apply(lambda x: x[:-9].replace('-','')) for d3 friendly format

def byDate(df, hidegroups=True, byContact=False):
  '''accepts msg dataframe and groups by month.'''
  msg = df.copy()
  if hidegroups: # -hidegroups change
    msg = msg[msg.cname.str.startswith('chat') != True]
  msg['yr'] = msg.date.apply(lambda x : x[:4])
  msg['mo'] = msg.date.apply(lambda x : x[5:7])
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  groupers = ['yr','mo','cname'] if byContact else ['yr','mo']
  mo_gr = msg.groupby(groupers)
  return getSumStats(mo_gr) 

def topN(ts, n=10):
  '''Finds the set of friends that have been in top top N some month'''
  ts['date'] = ts.yr.astype('str') + ts.mo.astype('str') + '01'
  keep = set() 
  for m in ts.date.unique():
    keep.update(ts[ts.date == m].sort('msg_len',ascending=False)[:10].cname)
  return list(keep) 

def panelPivot(ts):
  ret = ts[['date','cname','msg_len']].pivot(index='date',columns='cname', values='msg_len')
  return ret.fillna(0).reset_index()

def main(msg, n=10):
  '''returns a DF documenting your texting with best n friends over time.'''
  ts =  byDate(msg, byContact=True)
  keepers = topN(ts,10)
  ts['keep'] = ts.cname.apply(lambda x: x in keepers)
  ret = ts[ts.keep].sort('msg_len', ascending=False)
  #seaborn.pointplot(x='date',y='msg_len',hue='cname',data=ts)
  return panelPivot(ret)
