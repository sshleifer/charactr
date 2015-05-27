# Prepares a DF (that will be written to ts.csv).
# In this DF, each line is a contact, the x axis is time,
# and the y axis is characters exchanged

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
  '''accepts msg DF (returned by  chat_to_csv.writeChat()) and groups by hour.'''
  msg = df.copy()
  if hidegroups: 
    msg = msg[msg.cname.str.startswith('chat') != True]
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  msg['hour'] = msg.date.apply(lambda x : int(x[-8:-6])) 
  # NOTE: I would not cast that string to an int (will get one digit sometimes) - SS
  msg_groups = msg.groupby('hour')
  return getSumStats(msg_groups)
  
def byDate(df, hidegroups=True, byContact=False):
  '''accepts msg dataframe and groups by month.'''
  msg = df.copy()
  if hidegroups: # -hidegroups change
    msg = msg[msg.cname.str.startswith('chat') != True]
  msg['yr'] = msg.date.apply(lambda x : x[:4])
  msg['mo'] = msg.date.apply(lambda x : x[5:7])
  msg['ymd'] = msg.date.apply(lambda x: x[:10])
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  #groupers = ['yr','mo','cname'] if byContact else ['yr','mo']
  groupers = ['ymd','cname'] if byContact else ['ymd']
  date_grouped = msg.groupby(groupers)
  return getSumStats(date_grouped)

def topN(ts, n=10):
  '''NO LONGER BEING USED, BUT AN INTERESTING STRATEGY'''
  '''Finds the set of friends that have been in top N some month'''
  k = ts.groupby('cname').msg_len.agg(np.sum)
  return k
  print k.head()
  #ts['date'] = ts.yr.astype('str') + ts.mo.astype('str') + '01'
  keep = set() 
  for m in ts.ymd.unique():
    keep.update(ts[ts.date == m].sort('msg_len',ascending=False)[:10].cname)
  return list(keep) 

def panelPivot(ts):
  '''Flips the dataframe to long format to fill in zeroes during quiet months'''
  #TODO(SS): eliminate this. Its a stupid hack.
  ret = ts[['ymd','cname','msg_len']].pivot(index='ymd',columns='cname', values='msg_len')
  return ret.fillna(0).reset_index()

def timePanel(msg, besties):
  '''Returns a DF documenting your texting with best n friends over time.'''
  ts =  byDate(msg, byContact=True)
  ts['keep'] = ts.cname.apply(lambda x: x in besties)
  wide = panelPivot(ts[ts.keep]).set_index('ymd')
  wide['ymd'] = wide.index 
  panel = pd.melt(wide, id_vars=['ymd'])
  panel.columns = ['date','key','value'] # to play nice with js code
  return panel.set_index('key')
