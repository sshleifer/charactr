''' Reads in some tables from chat.db, joins and cleans them,
and then calls contacts.py to label phone numbers with contact names.
By Sam Shleifer, Peter Dewire since April 8, 2015.'''
from subprocess import call
from contacts import addresses
from figures import fig1
import numpy as np
import os
import pandas as pd
import sqlite3
from sys import argv
import time

CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")
BASE = 978307200

def byContact(msg):
  '''Group conversations by contact, and calculate summary stats'''
  if len(argv) > 1: # -hidegroups change
    msg = msg[msg.cname.str.startswith('chat') != True]
  gb= msg.groupby('cname')
  sums, means  = gb.agg(np.sum), gb.agg(np.mean)
  chars_sent = lambda x: np.sum(x['is_sent']*x['msg_len'])
  full = pd.DataFrame({'num':gb.size()})
  full['nsent'] = sums.is_sent
  full['msent'] = means.is_sent
  full['lensent'] = gb['is_sent','msg_len'].agg(chars_sent).is_sent
  full['totlen'] =  sums.msg_len
  full['lenrec'] = full.totlen - full.lensent
  full['nrec'] = full.num - full.nsent
  return full

def clean(old):
    '''Cleans DF columns'''
    msg = old.copy()
    timefix = lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x + BASE))
    msg['date'] = msg.date.map(timefix)
    msg['msg_len'] =  msg.text.map(lambda x: len(x) if x else 0)
    return msg

def writeChat():
  '''Writes message number,type. text, other person and date to msg.csv'''
  db = sqlite3.connect(CHAT_DB)
  msg_raw = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)
  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg = msg_raw.merge(full_chat, left_on='ROWID', right_on='message_id')

  msg['chat_id'] = msg.chat_identifier.map(lambda x: x.replace('+1','')) 
  clist = addresses()
  name = lambda cid: clist[cid] if cid in clist.keys() else cid
  msg['cname'] = msg.chat_id.map(name) 
  keep = ['ROWID_x','text','date','chat_id','is_sent', 'cname']
  return clean(msg[keep])

def main():
  if len(argv) > 2:
    print "USAGE: python chat_to_csv.py [-hidegroups]"
  elif len(argv) == 1:
    print '''Warning: Group chats will be labeled as chat followed by a long
    number.'''
  msg = writeChat()
  ppl = byContact(msg)
  names = msg.cname.unique()
  glen = len(filter(lambda x: x and x.startswith('chat'), names))
  ilen = len(filter(lambda x: x and not x.startswith('chat'), names))
  
  print 'Writing %d texts with %d individuals and %d groups to msg.csv and ppl.csv'%(len(msg),
      ilen, glen)
  #Write to Files
  msg.to_csv('msg.csv',encoding='utf-8')
  ppl.to_csv('ppl.csv', encoding='utf-8')
  fig1(msg, 'fig1.png')
  print 'Opening Histogram (fig1.png) and Scatterplot (in Safari).'
  return msg

if __name__ == '__main__':
  main()
