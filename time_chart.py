#New figures dealing with time and date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def getSumStats(gb):
  '''Number of characters sent and received by each group.'''
  sums = gb.agg(np.sum)
  ret = pd.DataFrame(sums.msg_len)
  ret['snt'] = sums.snt_chars
  ret['rec'] = sums.msg_len - sums.snt_chars
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
  
def byDate(df, hidegroups=True, byContact=False):
  '''accepts msg dataframe and groups by month.'''
  msg = df.copy()
  if hidegroups: # -hidegroups change
    msg = msg[msg.cname.str.startswith('chat') != True]
  msg['yr'] = msg.date.apply(lambda x : int(x[:4]))
  msg['mo'] = msg.date.apply(lambda x : int(x[5:7]))
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  groupers = ['yr','mo','cname'] if byContact else ['yr','mo']
  mo_gr = msg.groupby(groupers)
  return getSumStats(mo_gr) 



def topNFriends(ts, n=10):
  '''Finds the set of friends that have been in top top N some month'''
  ts['ym'] = ts.yr.astype('str') + '-' + ts.mo.astype('str')
  keep = set() 
  for m in ts.ym.unique():
    keep.update(ts[ts.ym == m].sort('msg_len',ascending=False)[:10].cname)
  return list(keep) 

def bestFriends(msg, n=10):
  '''returns a dataframe documenting your texting with best n friends
  over time.'''
  ts =  byDate(msg, byContact=True)
  keepers = topNFriends(ts,10)
  ts['keep'] = ts.cname.apply(lambda x: x in keepers)
  return ts[ts.keep].sort('msg_len', ascending=False)


# Cool seaborn plot after calling ` ts=bestFriends(msg)
#seaborn.pointplot(x='ym',y='msg_len',hue='cname',data=ts)
    
