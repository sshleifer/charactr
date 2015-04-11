# Reads in some tables from chat.db and joins.
# Sam Shleifer, Peter Dewire
# April 8, 2015.
import datetime as dt
import numpy as np
import os
import pandas as pd
import sqlite3
import time
from figures import fig1, fig2
CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")
BASE = 978307200
FIG_PATH = ['fig1.png','fig2.png']
###Random Debugging Tools
def find_unis(df):
  unis = {}
  for col in df.columns:
    try:
      unis[col] = len(df[col].unique())
    except TypeError:
      continue
  return unis

def getTabs(cursor):
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  return cursor.fetchall()

def tbl_to_df(tab_name, con):
  query = "SELECT * from " + tab_name
  df = pd.read_sql(query, con)
  return df

####Read in Chat
def timefix(since, base): 
  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(since + BASE))

def byChat(msg):
  '''Group conversations by contact'''
  gb = msg.groupby('chat_identifier')
  sums  = gb.agg(np.sum)
  means = gb.agg(np.mean)
  slen = gb[['is_sent', 'msg_len']].agg(lambda x: np.sum(x['is_sent']* x['msg_len']))
  full = pd.DataFrame() 
  full['num'] = gb.size()
  full['msent'] = means['is_sent']
  full['lensent'] = slen['is_sent']
  full['totlen'] = sums['msg_len']
  full['num_snt']= sums['is_sent']
  full['lenrec'] = full.totlen - full.lensent
  full['num_rec'] = full.size - full.num_snt
  return full

def writeChat():
  '''Writes message number,type. text, other person and date to msg.csv'''
  def clean(old):
    '''Cleans DF columns'''
    msg = old.copy()
    msg['date'] = msg.loc[:,'date'].apply(lambda x: timefix(x, BASE))
    msg['msg_len'] =  msg.loc[:,'text'].apply(lambda x: len(x) if x else 0)
    msg['snt_string'] = msg.loc[:,'is_sent'].apply(lambda x: 'sent' if x==1 else 'got') 
    return msg

  db = sqlite3.connect(CHAT_DB)
  msg = pd.read_sql("SELECT * from message", db)
  chat = pd.read_sql("SELECT * from chat", db)
  cmj =  pd.read_sql("SELECT * from chat_message_join", db)

  full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
  msg_final = pd.merge(msg, full_chat,left_on='ROWID', right_on='message_id')
  keep = ['ROWID_x','text','date','chat_identifier','is_sent']
  return clean(msg_final[keep])

def orig_addresses():
  '''Attempt to make table where names can be looked up using phone numbers.'''
  src = os.listdir(os.path.expanduser("~/Library/Application Support/AddressBook/Sources"))[0]
  database = os.path.expanduser(os.path.join("~/Library/Application Support",
    "AddressBook/Sources", src,
    "AddressBook-v22.abcddb"))
  connection = sqlite3.connect(database)
  ad = connection.cursor()
  adtabs = getTabs(ad) #For debugging
  numtab = pd.read_sql("""SELECT * FROM ZABCDPHONENUMBER
              LEFT OUTER JOIN ZABCDRECORD
              ON ZABCDPHONENUMBER.Z_PK = ZABCDRECORD.Z_PK""", connection)
  nt = numtab[['ZFULLNUMBER','ZFIRSTNAME','ZLASTNAME']]
  nt.colums=['number','fname','lname']
  return nt

# addresses() takes no parameters and returns a dictionary (nn_map) mapping
# phone numbers to contact names
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
            print "error, number not matched"              # should not happen
            num = '00000000000'
        
        # add to dictionary
        nn_map[num] = name

    print nn_map
    return nn_map


def main():
  msg = writeChat()
  ppl = byChat(msg)
  print 'Writing', len(msg), 'texts to msg.csv and ppl.csv'
  msg.to_csv('msg.csv',encoding='utf-8')
  ppl.to_csv('ppl.csv', encoding='utf-8')
  
  fig1(msg, FIG_PATH[0])
  fig2(ppl, FIG_PATH[1])
  print 'Creating two charts to', FIG_PATH[0], 'and', FIG_PATH[1], '.' 
  nums = addresses()
  mgd = msg.merge(nums, left_on='chat_identifier', right_on='ZFULLNUMBER',
      how='left')
  #ABOVE LINE IS BROKEN 

if __name__ == '__main__':
  main()
