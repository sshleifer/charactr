###  Reads in some tables from chat.db, joins and cleans them,
###  and then calls contacts.py to label phone numbers with contact names.
###  By Sam Shleifer, Peter Dewire since April 8, 2015.
from contacts import addresses
import datetime as dt
import numpy as np
import os
import pandas as pd
import sqlite3
from sys import argv
import time
from time_chart import timePanel

CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")
BASE = 978307200

def checkSavedData():
  keep = ['ROWID_x','text','date','chat_id','is_sent','cname']
  return pd.read_csv('msg.csv')[keep] if os.path.exists('msg.csv') else []
    

def byContact(msg):
  '''Group conversations by contact, and calculate summary stats'''
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  gb = msg.groupby('cname')
  sums, means  = gb.agg(np.sum), gb.agg(np.mean) 
  full = pd.DataFrame({'num':gb.size()})
  full['nsent'] = sums.is_sent
  full['msent'] = means.is_sent
  full['lensent'] = sums.snt_chars
  full['totlen'] =  sums.msg_len
  full['lenrec'] = full.totlen - full.lensent
  full['nrec'] = full.num - full.nsent
  full['start'] =  gb.date.agg(np.min)
  full['end'] =  gb.date.agg(np.max)
  return full

def clean(old):
    '''Cleans dataframe columns'''
    msg = old.copy()
    timefix = lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x + BASE))
    msg['date'] = msg.date.apply(timefix)
    msg['msg_len'] =  msg.text.fillna(0).apply(lambda x: len(x) if x else 0)
    return msg

def read_db():
  '''Reads text data from chat.db to a dataframe'''
  db = sqlite3.connect(CHAT_DB)
  msg_raw = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)
  return msg_raw, chat, cmj

def writeChat(saved_data):
  '''Writes message number,type. text, other person and date to msg, a df'''
  msg_raw,chat,cmj = read_db()
  #print msg_raw.head() 
  print '1.', chat.columns
  print '2.', cmj.columns
  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg = msg_raw.merge(full_chat, left_on='ROWID', right_on='message_id')
  
  msg['chat_id'] = msg.chat_identifier.apply(lambda x: x.replace('+1','')) 
  clist = addresses()
  def findName(cid):
    try:
      return clist[cid].rstrip()
    except KeyError:
      return cid if isinstance(cid, str) else 0

  msg['cname'] = msg.chat_id.apply(findName) 
  keep = ['ROWID_x','text','date','chat_id','is_sent','cname']
  msg = clean(msg[keep])
  if len(saved_data) > 0:
    #to support feature change after saving
    if 'msg_len' not in saved_data.columns:
      saved_data['msg_len'] =  saved_data.text.fillna(0).apply(lambda x: len(x) if x else 0)
    cutoff = saved_data.date.max()
    msg = pd.concat([saved_data, msg[msg.date > cutoff]])
  return msg

def main(hidegroups=True):
  print "being executed at", os.path.abspath('.')
  saved_data = checkSavedData()
  msg = writeChat(saved_data) #Read in, clean a dataframe of all messages
  if len(argv) <= 1 or hidegroups: 
    msg = msg[msg.cname.str.startswith('chat') != True]
  ppl = byContact(msg.copy()) #Collect metadata for each contact
  
  besties = list(ppl.sort('totlen',ascending=False).index[:10])
  ts = timePanel(msg, besties) 

  # Write csvs
  #msg.to_csv('msg.csv',encoding='utf-8')  # Removed for speed
  ts.to_csv('ts.csv')
  ppl.to_csv('ppl.csv', encoding='utf-8')

  ###Statistics for print statement
  names = msg.cname.fillna(0).unique()
  print filter(lambda x: isinstance(x, float), names)
  glen = len(filter(lambda x: x and x.startswith('chat'), names))
  ilen = len(filter(lambda x: x and not x.startswith('chat'), names))
  
  print '''Writing %d texts with %d individuals and %d groups since %s to ts.csv and
  ppl.csv in %s''' %(len(msg),ilen, glen,msg.date.min(), os.path.abspath('.'))
  #return msg for interactive use

if __name__ == '__main__':
  main()
