# Prepares a DF (that will be written to ts.csv).
# In this DF, each line is a contact, the x axis is time,
# and the y axis is characters exchanged
import numpy as np
import pandas as pd
from helpers.utils import filter_based_on_col
from types import *

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


def timePanel(msg, besties=False, topn=10):
  '''Returns a DF documenting your texting with best n friends over time.'''
  assert isinstance(msg, pd.DataFrame)
  ts =  byDate(msg, byContact=True)
  if not besties: besties = topN(ts, topn)
  ts = filter_based_on_col(ts, 'cname', lambda x: x in besties)[['cname', 'ymd', 'msg_len']]
  ts.columns = ['key','date','value']
  datestr = lambda x: str(x.date())
  full_range = map(datestr, pd.date_range(ts.date.min(), ts.date.max()))
  to_add = []
  for key in ts.key.unique():
    tmp = map(str, ts[ts.key == key].date.unique())
    to_add = to_add + [[key,d,0] for d in full_range if d not in tmp]


  #cut out early texts
  assert isinstance(ts, pd.DataFrame)
  dvals = ts.groupby('date').value.sum().to_frame()
  dvals['csum'] = dvals.value.cumsum()/dvals.value.sum()
  ts['date'] = ts.date.apply(str)
  return ts.set_index('key')
  #cutdate = str(dvals[dvals.csum > .01].index[0])
  #return ts[ts.date >= cutdate].set_index('key')
