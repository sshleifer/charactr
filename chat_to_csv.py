###  Reads in some tables from chat.db, joins and cleans them,
###  and then calls contacts.py to label phone numbers with contact names.
###  By Sam Shleifer, Peter Dewire since April 8, 2015.
from contacts import addresses
import numpy as np
import os
import pandas as pd
import sqlite3
from sys import argv
import time

CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")
BASE = 978307200

#@profile
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

#@profile
def clean(old):
    '''Cleans DF columns'''
    msg = old.copy()
    timefix = lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x + BASE))
    msg['date'] = msg.date.apply(timefix)
    msg['msg_len'] =  msg.text.apply(lambda x: len(x) if x else 0)
    return msg

#@profile
def read_db():
  '''Reads text data from chat.db to a dataframe'''
  db = sqlite3.connect(CHAT_DB)
  msg_raw = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)
  return msg_raw, chat, cmj

def writeChat():
  '''Writes message number,type. text, other person and date to msg, a df'''
  msg_raw,chat,cmj = read_db()
  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg = msg_raw.merge(full_chat, left_on='ROWID', right_on='message_id')

  msg['chat_id'] = msg.chat_identifier.apply(lambda x: x.replace('+1','')) 
  clist = addresses()
  
  def findName(cid):
    try:
      return clist[cid]
    except KeyError:
      return cid

  msg['cname'] = msg.chat_id.apply(findName) 
  keep = ['ROWID_x','text','date','chat_id','is_sent', 'cname']
  return clean(msg[keep])

#@profile
def main(hidegroups=False):
  print "being executed at", os.path.abspath('.')
  msg = writeChat() #Read in, clean a dataframe of all messages
  if len(argv) > 1 or hidegroups: 
    msg = msg[msg.cname.str.startswith('chat') != True]
  ppl = byContact(msg.copy()) #Collect metadata foreach contact

  ###Statistics for print statement
  names = msg.cname.unique()
  glen = len(filter(lambda x: x and x.startswith('chat'), names))
  ilen = len(filter(lambda x: x and not x.startswith('chat'), names))
 
  # Write csvs
  #msg.to_csv('msg.csv',encoding='utf-8')  # Removed for speed
  ppl.to_csv('ppl.csv', encoding='utf-8')
  #fig1(msg, 'fig1.png')

  print '''Writing %d texts with %d individuals and %d groups since %s to msg.csv and
  ppl.csv in %s''' %(len(msg),ilen, glen,msg.date.min(), os.path.abspath('.'))
  #return msg for interactive use

if __name__ == '__main__':
  main()
