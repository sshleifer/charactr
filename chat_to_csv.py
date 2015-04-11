# Reads in some tables from chat.db and joins.
# Sam Shleifer, Peter Dewire
# April 8, 2015.
from contacts import *
import datetime as dt
from figures import fig1, fig2
import numpy as np
import os
import pandas as pd
import re
import sqlite3
import time
CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")
BASE = 978307200
FIG_PATH = ['fig1.png','fig2.png']

def getTabs(cursor):
  '''Assists database navigation.'''
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  return cursor.fetchall()

####Read in Chat
def timefix(since, base): 
  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(since + BASE))

def byChat(msg):
  '''Group conversations by contact'''
  gb = msg.groupby('chat_identifier')
  sums  = gb.agg(np.sum)
  means = gb.agg(np.mean)
  slen = gb[['is_sent', 'msg_len']].agg(lambda x: np.sum(x['is_sent']* x['msg_len']))
  full = pd.DataFrame() 
  full['num'] = gb.size()
  full['msent'] = means['is_sent']
  full['lensent'] = slen['is_sent']
  full['totlen'] = sums['msg_len']
  full['num_snt']= sums['is_sent']
  full['lenrec'] = full.totlen - full.lensent
  full['num_rec'] = full.size - full.num_snt
  return full

def writeChat():
  '''Writes message number,type. text, other person and date to msg.csv'''
  def clean(old):
    '''Cleans DF columns'''
    msg = old.copy()
    msg['date'] = msg.loc[:,'date'].apply(lambda x: timefix(x, BASE))
    msg['msg_len'] =  msg.loc[:,'text'].apply(lambda x: len(x) if x else 0)
    msg['snt_string'] = msg.loc[:,'is_sent'].apply(lambda x: 'sent' if x==1 else 'got') 
    return msg

  db = sqlite3.connect(CHAT_DB)
  msg = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)

  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg_final = pd.merge(msg, full_chat,left_on='ROWID', right_on='message_id')
  keep = ['ROWID_x','text','date','chat_identifier','is_sent']
  return clean(msg_final[keep])

def main():
  msg = writeChat()
  ppl = byChat(msg)
  print 'Writing', len(msg), 'texts to msg.csv and ppl.csv'
  msg.to_csv('msg.csv',encoding='utf-8')
  ppl.to_csv('ppl.csv', encoding='utf-8')

  fig1(msg, FIG_PATH[0])
  fig2(ppl, FIG_PATH[1])
  print 'Creating two charts to', FIG_PATH[0], 'and', FIG_PATH[1], '.' 

if __name__ == '__main__':
  main()
