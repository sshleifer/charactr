###  Reads in some tables from chat.db, joins and cleans them,
###  and then calls contacts.py to label phone numbers with contact names.
###  By Sam Shleifer, Peter Dewire since April 8, 2015.
from contacts import addresses, groupbyContact
import datetime as dt
from helpers.utils import filterDF, msgLen
import numpy as np
import os
import pandas as pd
import sqlite3
from sys import argv
import time
from time_chart import timePanel
from word_cloud import writeWords

CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")
MY_MOBILE_BACKUP = os.path.expanduser("~/Library/Application Support/MobileSync/Backup/54585babaa97cc69042ccbc493d68a229ac8babd/3d0d7e5fb2ce288813306e4d4636395e047a3d28")
PTH = '3d0d7e5fb2ce288813306e4d4636395e047a3d28'
MOBILE_BASE = os.path.expanduser('~/Library/Application Support/MobileSync/Backup/')
BASE = 978307200

def queryDB(db_path):
  '''Writes message number,type. text, other person and date to msg, a df'''
  try:
    db = sqlite3.connect(db_path)
    msg_raw = pd.read_sql("SELECT * from message", db)
    chat = pd.read_sql("SELECT * from chat", db)
    cmj =  pd.read_sql("SELECT * from chat_message_join", db)
  except Exception as e:
    print db_path, 'on path: \n', e
    return []
  ### Merge db reads
  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg = msg_raw.merge(full_chat, left_on='ROWID', right_on='message_id')
  ### Find contact names and clean columns
  msg['chat_id'] = msg.chat_identifier.apply(lambda x: x.replace('+1','')) 
  clist = addresses()
  def findName(cid):
    try:
      return clist[cid].rstrip()
    except KeyError:
      return cid.rstrip()
 
  msg['cname'] = msg.chat_id.apply(findName) 
  date_cut = lambda x: dt.datetime.fromtimestamp(x + BASE)
  msg['tstamp'] = msg.date.apply(date_cut)
  msg['day'] = msg.tstamp.apply(lambda x: x.date())
  msg['msg_len'] =  msg.text.fillna('').apply(msgLen)
  keep = ['ROWID_x','text','tstamp','chat_id','is_sent','cname','msg_len','day']
  return msg[keep]

def readDB(test_path=False):
  '''Reads text data from all possible iPhone backups.
    Falls back on iMessage (which is smaller).'''
  backups = [queryDB(os.path.join(x[0],PTH)) for x in os.walk(MOBILE_BASE) if PTH in x[2]]
  if not backups: 
    print 'Could not find iPhone backup'
  if test_path: 
    backups.append(queryDB(test_path))
  backups.append(queryDB(CHAT_DB))
  return filter(lambda x: len(x) > 0, backups) 

def checkSavedData():
  '''Get saved data if it exists.''' 
  keep = ['ROWID_x','text','tstamp','chat_id','is_sent','cname']
  return pd.read_csv('msg.csv')[keep] if os.path.exists('msg.csv') else []

def concatSaved(msg, saved_data):
  '''Adds saved data to extracted data, if saved data exists.'''
  str2date = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
  saved_data['tstamp'] = saved_data.tstamp.apply(str2date) 
  if 'msg_len' not in saved_data.columns:
    saved_data['msg_len'] =  saved_data.text.fillna(0).apply(msgLen)
  cutoff = saved_data.tstamp.max()
  return pd.concat([saved_data, msg[msg.tstamp > cutoff]])

def writeChat(saved_data=[]):
  '''combine and deduplicate the various db reads'''
  df = pd.concat(readDB()).drop_duplicates(subset=['day','cname','text']) 
  #TODO (SS): how slow is above?
  return concatSaved(df,saved_data) if saved_data else df

def tryCSV(df, path):
  try:
    df.to_csv(path, encoding='utf-8')
  except Exception as e:
    print 'ERROR on CSV WRITE to %s:', e % (path)
    print 'DF:', df 

def main(hidegroups=True, use_saved=False):
  print "being executed at", os.path.abspath('.')
  saved_data = checkSavedData() if use_saved else []
  msg = writeChat(saved_data)
  if len(argv) <= 1 or hidegroups: 
    msg = msg[msg.cname.str.startswith('chat') != True]
  ppl = groupbyContact(msg.copy()).sort('totlen', ascending=False) 
  print ppl.head()
  besties = map(lambda x: x.rstrip(),ppl.index[:10])
  print besties
  ts = timePanel(msg, besties) 
  
  tryCSV(msg, 'msg.csv')
  tryCSV(ts, 'ts.csv')
  tryCSV(ppl, 'ppl.csv')

  # create word_cloud.txt
  if not os.path.isfile('word_cloud.txt'):
    writeWords(msg)
  else:
    print 'not rewriting word_cloud.txt'

  ###Statistics for print statement
  names = msg.cname.fillna(0).unique()
  glen = len(filter(lambda x: x and x.startswith('chat'), names))
  print '''Writing %d texts with %d individuals and %d groups since %s to ts.csv and
    ppl.csv in %s''' %(len(msg),len(names) - glen, glen,msg.tstamp.min(), os.path.abspath('.'))
  # return msg # for interactive use

if __name__ == '__main__':
  main()
