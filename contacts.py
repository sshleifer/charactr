import numpy as np
import os
import pandas as pd
import re
import sqlite3
def getTabs(cursor):
  '''Assists database navigation.'''
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  return cursor.fetchall()


PATH = "~/Library/Application Support/AddressBook/AddressBook-v22.abcddb"
src = os.listdir(os.path.expanduser("~/Library/Application Support/AddressBook/Sources"))[0]
BACKUP = os.path.expanduser(os.path.join("~/Library/Application Support",
    "AddressBook/Sources", src,
    "AddressBook-v22.abcddb"))
 


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
# addresses() takes no parameters and returns a {number: name} dictionary
def addresses():
  cl1 = getData(PATH) 
  cl2 = getData(BACKUP)
  contact_list = cl1 + cl2 
  def get_name(row):
    return row[0] if row[0] == row[1] else ' '.join(row[0:2])
    
  clist = [x.replace('+1','').split() for x in contact_list]
  cdict =  {x[-1]:get_name(x) for x in clist} 

  return cdict 

