#New figures dealing with time and date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def getSumStats(gb):
  '''Number of characters sent and received by each group.'''
  sums = mo_gr.agg(np.sum)
  ret = pd.DataFrame(sums.msg_len)
  ret['snt'] = sums.snt_chars
  ret['rec'] = sums.msg_len - sums.snt_chars
  return ret

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
  
def byDate(df, hidegroups=True):
  '''accepts msg dataframe and groups by month.'''
  msg = df.copy()
  if hidegroups: # -hidegroups change
    msg = msg[msg.cname.str.startswith('chat') != True]
  msg['yr'] = msg.date.apply(lambda x : int(x[:4]))
  msg['mo'] = msg.date.apply(lambda x : int(x[5:7]))
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  mo_gr = msg.groupby(['yr','mo'])
  return getSumStats(gb) 
