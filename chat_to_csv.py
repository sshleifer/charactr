###  Reads in some tables from chat.db, joins and cleans them,
###  and then calls contacts.py to label phone numbers with contact names.
###  By Sam Shleifer, Peter Dewire since April 8, 2015.
from contacts import addresses, groupbyContact
import datetime as dt
from helpers.utils import filterDF, msgLen,checkSavedData, concatSaved
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
    hdl =  pd.read_sql("SELECT * from handle", db)

  except Exception as e:
    print 'Non-Fatal db error at %s \n', e % (db_path)
    return []
  ### Merge db reads
  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg = msg_raw.merge(full_chat, left_on='ROWID', right_on='message_id')
  msg  = msg.merge(hdl, left_on='handle_id', right_on='ROWID')
  ### Find contact names and clean columns
  date_cut = lambda x: dt.datetime.fromtimestamp(x + BASE)
  msg['tstamp'] = msg.date.apply(date_cut)
  msg['day'] = msg.tstamp.apply(lambda x: x.date())
  msg['msg_len'] =  msg.text.fillna('').apply(msgLen)
  return msg
  #return msg[keep]

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

def writeChat(saved_data=[]):
  '''combine and deduplicate the various db reads'''
  msg = pd.concat(readDB()).drop_duplicates(subset=['day','chat_identifier','text']) 
  clist = addresses(msg)
  def findName(cid):
    cid = cid.replace('+1','')
    try:
      return clist[cid].rstrip()
    except KeyError:
      return cid.rstrip()
  msg['cname'] = msg.chat_identifier.apply(findName) 
  return concatSaved(msg,saved_data) if saved_data else msg

def tryCSV(df, path):
  try:
    df.to_csv(path, encoding='utf-8')
  except Exception as e:
    print 'ERROR on CSV WRITE to %s:', e, df % (path)

def main(hidegroups=True, use_saved=False):
  print "being executed at", os.path.abspath('.')
  saved_data = checkSavedData() if use_saved else []
  msg = writeChat(saved_data)
  print msg.shape
  if len(argv) <= 1 or hidegroups: 
    msg = filterDF(msg, 'cname', lambda x: not x.startswith('chat'))
  ppl = groupbyContact(msg.copy()).sort('totlen', ascending=False) 
  print ppl.head()
  besties = map(lambda x: x.rstrip(),ppl.index[:10])
  print 'besties:', besties
  ts = timePanel(msg, besties) 
  
  keep = ['text','tstamp','is_sent','cname']
  tryCSV(msg[keep], 'msg.csv')
  tryCSV(ts, 'ts.csv')
  tryCSV(ppl, 'ppl.csv')

  # create word_cloud.txt
  writeWords(msg)

  print '''Found %d texts in %d conversations since %s.''' % (len(msg),len(msg.cname.unique()), msg.tstamp.min())
  #return msg # for interactive use

if __name__ == '__main__':
  main()
