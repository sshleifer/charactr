import numpy as np
import os
import pandas as pd
import re
import sqlite3
import fnmatch

PATH = "~/Library/Application Support/AddressBook/AddressBook-v22.abcddb"

def extractContacts(path):
  '''Get Contact Data from PHONENUMBER, RECORD Tables. As in icloud_query.py'''
  ADDRESS_DB = os.path.expanduser(path)
  ad_db = sqlite3.connect(ADDRESS_DB)
  jn = pd.read_sql("""SELECT ZFULLNUMBER, ZSORTINGFIRSTNAME FROM ZABCDPHONENUMBER
              LEFT OUTER JOIN ZABCDRECORD
              ON ZABCDPHONENUMBER.ZOWNER = ZABCDRECORD.Z_PK""", ad_db)
  clean =  lambda x: ''.join(c for c in x if '0' <= c <= '9')[-10:]
  cstart = zip(map(clean, jn.ZFULLNUMBER), jn.ZSORTINGFIRSTNAME)
  clist = {x[0]: x[1][:len(x[1])/2] for x in cstart} 
  return clist

def addresses():
  '''create the {number: name} dictionary from contacts app, or phone backup.'''
  contact_list = extractContacts(PATH)
  srcs = os.path.expanduser("~/Library/Application Support/AddressBook/Sources")
  if os.path.exists(srcs):
    cl2 = {}
    SRC = os.listdir(srcs)[0]
    BACKUP = os.path.expanduser(os.path.join("~/Library/Application Support",
      "AddressBook/Sources", SRC,
      "AddressBook-v22.abcddb"))
    cl2 = extractContacts(BACKUP)
    contact_list.update(cl2)
  return contact_list
  #contact_list += cl2 
  #clist = [x.replace('+1','').split() for x in contact_list]
  #return {x[-1][-10:]:parseName(x) for x in clist} 
