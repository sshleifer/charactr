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

####Read in Chat
def timefix(since, base): 
  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(since + BASE))

def byContact(msg):
  '''Group conversations by contact'''
  gb = msg.groupby('cname')
  sums  = gb.agg(np.sum)
  means = gb.agg(np.mean)
  slen = gb[['is_sent', 'msg_len']].agg(lambda x: np.sum(x['is_sent']* x['msg_len']))
  full = pd.DataFrame() 
  full['num'] = gb.size()
  full['msent'] = means['is_sent']
  full['num_snt']= sums['is_sent']
  full['lensent'] = slen['is_sent']
  full['totlen'] = sums['msg_len']
  full['lenrec'] = full.totlen - full.lensent
  full['num_rec'] = full.num - full.num_snt
  return full

def mapName(cid, clist, gen):
  #TODO Why do these following 2 lines cause group* not to appear in viz?
  if len(argv) > 1 and cid.startswith('chat'):  
    return "group" + str(gen.next())
  elif cid in clist.keys():  return clist[cid]
  elif cid[-10:] in clist.keys():
    return clist[cid[-10:]]
  elif len(cid) >= 11 and cid[-11:] in clist.keys():
    return clist[cid[-11:]]
  else: return cid

def firstn(n):
  '''To generate shorter numbers for chats. A temporary hack.'''
  for i in range(n):
    yield i

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
  #SQLITE joins are slower than pandas joins on my machine
  #TODO: Time following code on other machines
  #msg = pd.read_sql('''SELECT * from message as msg 
  #    LEFT OUTER JOIN CHAT_MESSAGE_JOIN as cmj
  #    on msg.ROWID = cmj.message_id 
  #    LEFT OUTER JOIN CHAT as ch
  #    on cmj.chat_id = ch.ROWID;
  #    ''', db)

  msg_raw = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)
  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg = msg_raw.merge(full_chat, left_on='ROWID', right_on='message_id')
  
  msg['chat_id'] = msg.chat_identifier.map(lambda x: x.replace('+1','')) 
  CLIST = addresses()
  gen = firstn(len(msg))
  msg['cname'] = msg.chat_id.map(lambda x: mapName(x, CLIST, gen)) 
  #msg['cname'] = chatNums(list(msg.cname))
  keep = ['ROWID_x','text','date','chat_id','is_sent', 'cname']
  return clean(msg[keep])

def main():
  msg = writeChat()
  ppl = byContact(msg)
  print 'Writing %d texts from %d different contacts to msg.csv and ppl.csv'%(len(msg),len(ppl))
  msg.to_csv('msg.csv',encoding='utf-8')
  ppl.to_csv('ppl.csv', encoding='utf-8')
  fig1(msg, 'fig1.png')
  print 'Created Histogram at fig1.png.'
  print 'Opening index.html in Safari to see Figure 2.'
  return msg

if __name__ == '__main__':
  main()
