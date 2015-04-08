'''Reads in some tables from chat.db and joins.
Sam Shleifer, April 8, 2015.'''
from os import path
import pandas as pd
import sqlite3
###Random Debugging Tools
def find_unis(df):
  unis = {}
  for col in df.columns:
    try:
      unis[col] = len(df[col].unique())
    except TypeError:
      continue
  return unis

def getTabs(c):
  c.execute("SELECT name FROM sqlite_master WHERE type='table';")
  return c.fetchall()

####Read in Chat
def writeChat():
  '''Writes message number,type. text, other person and date to msg.csv'''
  CHAT_DB = path.expanduser("~/Library/Messages/chat.db")
  db = sqlite3.connect(CHAT_DB)
  msg = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)
  c2 = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  c3 = pd.merge(msg, c2,left_on='ROWID', right_on='message_id')
  keep = ['ROWID_x','text','date','chat_identifier','is_sent']
  print 'Writing', len(c3), 'texts to msg.csv...'
  c3[keep].to_csv('msg.csv',encoding='utf-8') 

if __name__ == '__main__':
  writeChat()
