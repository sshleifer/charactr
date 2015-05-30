# Prepares a DF (that will be written to ts.csv).
# In this DF, each line is a contact, the x axis is time,
# and the y axis is characters exchanged
import numpy as np
import pandas as pd

def filterDF(df, col, bool_func):
  df['keep'] = df[col].apply(bool_func)
  return df[df.keep].drop('keep', 1)

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
  msg['hour'] = msg.tstamp.apply(lambda x : x.hour) 
  msg_groups = msg.groupby('hour')
  return getSumStats(msg_groups)
  
def byDate(df, hidegroups=True, byContact=False):
  '''accepts msg dataframe and groups by month.'''
  msg = df.copy()
  if hidegroups: # -hidegroups change
    msg = msg[msg.cname.str.startswith('chat') != True]
  msg['ymd'] = msg.tstamp.apply(lambda x: x.date())
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  groupers = ['ymd','cname'] if byContact else ['ymd']
  date_grouped = msg.groupby(groupers)
  return getSumStats(date_grouped)

def topN(ts, n=4):
  '''NO LONGER BEING USED, BUT AN INTERESTING STRATEGY'''
  '''Finds the set of friends that have been in top N some month'''
  keep = set() 
  ts['mo'] = ts.ymd.apply(lambda x: x.month)
  months = list(ts.mo.unique())
  for m in months:
    new_names = ts[ts.mo == m].sort('msg_len',ascending=False)[:n].cname
    keep.update(new_names)
  return list(keep) 

def panelPivot(ts):
  '''Flips the dataframe to long format to fill in zeroes during quiet months'''
  #TODO(SS): eliminate this. Its a stupid hack.
  ret = ts[['ymd','cname','msg_len']].pivot(index='ymd',columns='cname', values='msg_len')
  return ret.fillna(0).reset_index()

def timePanel(msg, besties=False, topn=10):
  '''Returns a DF documenting your texting with best n friends over time.'''
  ts =  byDate(msg, byContact=True)
  if not besties:
    besties = topN(ts, topn) 
  
  ts = filterDF(ts,  'cname', lambda x: x in besties)
  #ts['keep'] = ts.cname.apply(lambda x: x in besties)
  wide = panelPivot(ts).set_index('ymd')
  wide['ymd'] = wide.index 
  panel = pd.melt(wide, id_vars=['ymd'])
  panel['ymd'] = panel['ymd'].apply(lambda x: str(x.date()))

  panel.columns = ['date','key','value'] # to play nice with js code
  return panel.set_index('key')
