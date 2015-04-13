import numpy as np
import os
import pandas as pd
import sqlite3
import fnmatch

PATH = "~/Library/Application Support/AddressBook/AddressBook-v22.abcddb"
def possDB():
  '''Experimental attempt at finding all .abcddb files in file system.'''
  matches = []
  for root, dirnames, filenames in os.walk('~/Library'):
    for filename in fnmatch.filter(filenames, '*.abcddb'):
      matches.append(os.path.join(root, filename))
  return matches

def getTabs(cursor):
  '''Assists database navigation.'''
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  return [x[0] for x in cursor.fetchall()]

def newData(ad_db):
  '''Get Contact Data from PHONENUMBER, RECORD Tables. As in icloud_query.py'''
  jn = pd.read_sql("""SELECT ZFULLNUMBER, ZSORTINGFIRSTNAME FROM ZABCDPHONENUMBER
              LEFT OUTER JOIN ZABCDRECORD
              ON ZABCDPHONENUMBER.ZOWNER = ZABCDRECORD.Z_PK""", ad_db)
  cstart = zip(jn.ZFULLNUMBER, jn.ZSORTINGFIRSTNAME)
  clist = {x[0]: x[1][:len(x[1])/2] for x in cstart} 
  # TODO(SS) Clean x[0] (the phone number)
  return clist

def allData(cursor):
  for table in getTabs(cursor):
    cursor.execute("SELECT * FROM " + table)
    k = cursor.fetchall()
    print table, ': (10 rows)'
    print '**************'
    try:
      print k[:10]
    except IndexError:
      print k

def getContactData(path):
  '''returns a series of <firstname> <lastname> <phonenumber> <phonenumber> strings.
  FROM ZSTRING FOR INDEXING'''
  ADDRESS_DB = os.path.expanduser(path)
  ad_db = sqlite3.connect(ADDRESS_DB)
  ad_curs = ad_db.cursor()  #For Debugging
  adtabs = getTabs(ad_curs) #For Debugging
  query = "SELECT ZSTRINGFORINDEXING FROM ZABCDCONTACTINDEX"
  try:
    contact_list = pd.read_sql(query, ad_db)
    return list(contact_list.ZSTRINGFORINDEXING)
  except DatabaseError as db:
    print db
    return []

def addresses():
  '''create the {number: name} dictionary.'''
  contact_list = getContactData(PATH)
  srcs = os.path.expanduser("~/Library/Application Support/AddressBook/Sources")
  cl2 = []
  if os.path.exists(srcs):
    SRC = os.listdir(srcs)[0]
    BACKUP = os.path.expanduser(os.path.join("~/Library/Application Support",
      "AddressBook/Sources", SRC,
      "AddressBook-v22.abcddb"))
    cl2 = getContactData(BACKUP)
  
  contact_list += cl2 

  def parseName(row):
    if len(row) == 1: 
      return row[0]
    try:
      return row[0] if row[0] == row[1] else ' '.join(row[0:2])
    except:
      return ''

  clist = [x.replace('+1','').split() for x in contact_list]
  return {x[-1][-10:]:parseName(x) for x in clist} 
