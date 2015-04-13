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
  return cursor.fetchall()

def getData(path):
  '''returns a series of <firstname> <lastname> <phonenumber> <phonenumber> strings.'''
  ADDRESS_DB = os.path.expanduser(path)
  ad_db = sqlite3.connect(ADDRESS_DB)
  ad_curs = ad_db.cursor()
  adtabs = getTabs(ad_curs)
  query = "SELECT ZSTRINGFORINDEXING FROM ZABCDCONTACTINDEX"
  try:
    contact_list = pd.read_sql(query, ad_db)
    return list(contact_list.ZSTRINGFORINDEXING)
  except DatabaseError as db:
    print db
    return []

def addresses():
  '''create the {number: name} dictionary.'''
  contact_list = getData(PATH)
  if len(contact_list) == 0:
    srcs = os.path.expanduser("~/Library/Application Support/AddressBook/Sources")
    if os.path.exists(srcs):
      SRC = os.listdir(srcs)[0]
      BACKUP = os.path.expanduser(os.path.join("~/Library/Application Support",
        "AddressBook/Sources", SRC,
        "AddressBook-v22.abcddb"))
      contact_list = getData(BACKUP)
    else:
      return {}
  
  def parseName(row):
    return row[0] if row[0] == row[1] else ' '.join(row[0:2])
    
  clist = [x.replace('+1','').split() for x in contact_list]
  return {x[-1][-10:]:parseName(x) for x in clist} 
