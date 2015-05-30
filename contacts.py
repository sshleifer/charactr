'''Reads in addresses from DB stored at path, or backup, 
to label phone numbers.'''
import os
import pandas as pd
import numpy as np
import sqlite3
import sys

PATH = os.path.expanduser("~/Library/Application Support/AddressBook/AddressBook-v22.abcddb")
SRCS = os.path.expanduser("~/Library/Application Support/AddressBook/Sources")

def extractContacts(path):
  '''Get Contact Data from PHONENUMBER, RECORD Tables. As in icloud_query.py'''
  try:
    ad_db = sqlite3.connect(os.path.expanduser(path))
  except:
    print "INVALID PATH"
    return {}
  try:
    jn = pd.read_sql("""SELECT ZFULLNUMBER, ZSORTINGFIRSTNAME FROM ZABCDPHONENUMBER
              LEFT OUTER JOIN ZABCDRECORD
              ON ZABCDPHONENUMBER.ZOWNER = ZABCDRECORD.Z_PK""", ad_db)
    clean =  lambda x: ''.join(c for c in x if '0' <= c <= '9')[-10:]
    cstart = zip(map(clean, jn.ZFULLNUMBER), jn.ZSORTINGFIRSTNAME)
    clist = {x[0]: x[1][:len(x[1])/2] for x in cstart} 
    return clist
  except pd.io.sql.DatabaseError as e:
    print e, "failed on:", path
    return {}

def addresses():
  '''create the {number: name} dictionary from contacts app, or phone backup.'''
  contact_list = extractContacts(PATH)
  if os.path.exists(SRCS):
    BACKUPS = [os.path.expanduser(os.path.join("~/Library/Application Support",
      "AddressBook/Sources", source,
      "AddressBook-v22.abcddb")) for source in os.listdir(SRCS)]
    for bu in BACKUPS: 
      contact_list.update(extractContacts(bu))
    if not contact_list:
      print "Contacts: checked %s and %s" % (PATH, " ".join(BACKUPS))
      print "NO CONTACTS FOUND"
  return contact_list

def groupbyContact(msg):
  '''Group conversations by contact, and calculate summary stats'''
  msg['snt_chars'] = msg['is_sent'] * msg['msg_len']
  gb = msg.groupby('cname')
  sums, means  = gb.agg(np.sum), gb.agg(np.mean) 
  ppl = pd.DataFrame({'num':gb.size()})
  ppl['nsent'] = sums.is_sent
  ppl['msent'] = means.is_sent
  ppl['lensent'] = sums.snt_chars
  ppl['totlen'] =  sums.msg_len
  ppl['lenrec'] = ppl.totlen - ppl.lensent
  ppl['nrec'] = ppl.num - ppl.nsent
  ppl['start'] =  gb.tstamp.agg(np.min)
  ppl['end'] =  gb.tstamp.agg(np.max)
  return ppl

