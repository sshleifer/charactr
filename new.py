# Reads in some tables from chat.db and joins.
# Sam Shleifer, Peter Dewire
# April 8, 2015.

import re
import os
import pandas as pd
import sqlite3
CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")

###Random Debugging Tools
def find_unis(df):
  unis = {}
  for col in df.columns:
    try:
      unis[col] = len(df[col].unique())
    except TypeError:
      continue
  return unis

# takes a cursor c
def getTabs(c):
  c.execute("SELECT name FROM sqlite_master WHERE type='table';")
  return c.fetchall()

def tbl_to_df(tab_name, con):
  query = "SELECT * from " + tab_name
  df = pd.read_sql(query, con)
  return df

####Read in Chat
def writeChat():
  '''Writes message number,type. text, other person and date to msg.csv'''
  db = sqlite3.connect(CHAT_DB)
  msg = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)

  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg_final = pd.merge(msg, full_chat,left_on='ROWID', right_on='message_id')
  keep = ['ROWID_x','text','date','chat_identifier','is_sent']
  print 'Writing', len(msg_final), 'texts to msg.csv...'
  msg_final[keep].to_csv('msg.csv', encoding='utf-8') 
  return msg_final[keep]

def addresses_orig():
  source = os.listdir(os.path.expanduser("~/Library/Application Support/AddressBook/Sources"))[0]
  database = os.path.expanduser(os.path.join("~/Library/Application Support",
    "AddressBook/Sources", source,
    "AddressBook-v22.abcddb"))
  connection = sqlite3.connect(database)
  ad = connection.cursor()
  adtabs = getTabs(ad)
  numtab = pd.read_sql("""SELECT * FROM ZABCDPHONENUMBER
              LEFT OUTER JOIN ZABCDRECORD
              ON ZABCDPHONENUMBER.Z_PK = ZABCDRECORD.Z_PK""", connection)
  nt = numtab[['ZFULLNUMBER','ZFIRSTNAME','ZLASTNAME']]
  nt.colums=['number','fname','lname']
  return nt

# issues: see trello
def addresses():
    path = "~/Library/Application Support/AddressBook/AddressBook-v22.abcddb"
    ADDRESS_DB = os.path.expanduser(path)
    ad_db = sqlite3.connect(ADDRESS_DB)
    ad_curs = ad_db.cursor()
    adtabs = getTabs(ad_curs)
    query = "SELECT ZSTRINGFORINDEXING FROM ZABCDCONTACTINDEX"

    # contact_list is a Series of strings that are (usually):
    #    'firstname lastname phonenumber phonenumber'
    contact_list = pd.read_sql(query, ad_db)
    name_pattern = re.compile("[a-z]* [a-z]*")
    num_pattern = re.compile("[2-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]")

    # name, number dictionary
    nn_map = {}
    
    for i in range(2, len(contact_list)):
        # get string
        t = contact_list.ix[i]
        s = t[0]

        # match name
        m = name_pattern.search(s)
        name = s[m.start():m.end()]
        
        # match number
        m = num_pattern.search(s)
        if m:
            num = s[m.start():m.end()]
        else:
            print "error, number not matched"
            num = '00000000000'
        
        # add to dictionary
        nn_map[num] = name

    print nn_map


def main():
  #msg = writeChat()
  nums = addresses()
  #mgd = msg.merge(nums, left_on='chat_identifier', right_on='ZFULLNUMBER',
  #    how='left')
   
if __name__ == '__main__':
    main()
