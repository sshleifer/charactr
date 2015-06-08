'''Reads in addresses from DB stored at path, or backup, 
to label phone numbers.'''
from os.path import expanduser as eu
import os
import pandas as pd
import numpy as np
import sqlite3
import sys

COMP_PATH = eu("~/Library/Application Support/AddressBook/AddressBook-v22.abcddb")

ENDING = "AddressBook-v22.abcddb"
SRCS = eu("~/Library/Application Support/AddressBook/Sources")
MO_PTH = '31bb7ba8914766d4ba40d6dfb6113c8b614be442'
MO_BASE = eu('~/Library/Application Support/MobileSync/Backup/')

def extractContacts(path):
  '''Get Contact Data from PHONENUMBER, RECORD Tables. As in icloud_query.py'''
  try:
    ad_db = sqlite3.connect(path)
    jn = pd.read_sql("""SELECT ZFULLNUMBER, ZSORTINGFIRSTNAME FROM ZABCDPHONENUMBER
              LEFT OUTER JOIN ZABCDRECORD
              ON ZABCDPHONENUMBER.ZOWNER = ZABCDRECORD.Z_PK""", ad_db)
    clean =  lambda x: ''.join(c for c in x if '0' <= c <= '9')[-10:]
    cstart = zip(map(clean, jn.ZFULLNUMBER), jn.ZSORTINGFIRSTNAME)
    clist = {x[0]: x[1][:len(x[1])/2] for x in cstart} 
    return clist
  except pd.io.sql.DatabaseError as e:
    print "Non-fatal DB error ON path: ", path
    return {}

def backupContacts(path):
  '''makes {number: name} dict from iphone backup '''
  try:
    db = sqlite3.connect(path)
    sql_stm = 'SELECT c15Phone, c0First, c1Last, c6Organization from ABPersonFullTextSearch_content'
    jn = pd.read_sql(sql_stm, db)

    jn = jn.applymap(lambda x: '' if x == None else x)
    clean = lambda x: ''.join(c for c in x if '0' <= c <= '9')[-17:-7]
    cstart = zip(map(clean, jn.c15Phone), jn.c0First, jn.c1Last)
    clist = {x[0]: x[1] + ' ' + x[2] for x in cstart}
    return clist, True      # always return true?
  # want better except
  except Exception:
    print "Error in backupContacts with path: ", path
    return {}, False


def addresses():
  '''create the {number: name} dictionary from contacts app, or phone backup.'''
  success = False       # so we only call backupContacts once
  contact_list = extractContacts(COMP_PATH)
  backups = [os.path.join(MO_BASE, x[0], MO_PTH) for x in os.walk(MO_BASE) if MO_PTH in x[2]]
  # print backups
  if os.path.exists(SRCS):
    backups = backups + [os.path.join(SRCS,mid,ENDING) for mid in os.listdir(SRCS)]
  for bu in backups: 
    if not success and MO_PTH in bu:
      new_cdict, success = backupContacts(bu)
      contact_list.update(new_cdict)
    else:
        contact_list.update(extractContacts(bu))
  if not contact_list:
    print "Contacts: checked", COMP_PATH, backups 
    print "NO CONTACTS FOUND"
  return contact_list

def groupbyContact(msg):
  '''Group conversations by contact, and calculate summary stats'''
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  msg['date'] = msg.tstamp.apply(lambda x: x.date())
  gb = msg.groupby('cname')
  sums, means  = gb.agg(np.sum), gb.agg(np.mean) 
  ppl = pd.DataFrame({'num':gb.size()})
  ppl['nsent'] = sums.is_sent
  ppl['msent'] = means.is_sent
  ppl['lensent'] = sums.snt_chars
  ppl['totlen'] =  sums.msg_len
  ppl['lenrec'] = ppl.totlen - ppl.lensent
  ppl['nrec'] = ppl.num - ppl.nsent
  ppl['start'] =  gb.date.agg(np.min)
  ppl['end'] =  gb.date.agg(np.max)
  return ppl
