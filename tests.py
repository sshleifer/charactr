import datetime as dt
import pandas as pd
from subprocess import call
from sys import argv

from contacts import groupbyContact
from chat_to_csv import *
from time_chart import timePanel


def testMsg(path):
  msg = pd.read_csv(path)
  str2date = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
  str2date2 = lambda x: dt.datetime.strptime(x, '%m/%d/%Y %H:%M:%S')
  try:
    msg['tstamp'] = msg.tstamp.apply(str2date)
  except ValueError:
    msg['tstamp'] = msg.tstamp.apply(str2date2)
  ppl = groupbyContact(msg.copy()).sort('totlen', ascending=False) 
  print ppl.head()
  besties = map(lambda x: x.rstrip(),ppl.index[:10])
  print besties
  ts = timePanel(msg, besties) 
  
  # Write csvs
  tryCSV(msg, 'msg.csv')
  tryCSV(ts, 'ts.csv')
  tryCSV(ppl, 'ppl.csv')
  #call('open -a Safari index.html')


BAD_PATH = os.path.expanduser("~/Library/Application Support/MobileSync/Backup/54585babaa    97cc69042ccbc493d68a229ac8babd/3d0d7e5fb2ce288813306e4d4636395e047a3d28")

def testQuery(path=BAD_PATH):
 assert (not queryDB(BAD_PATH))

def testRead(path):
  print 'testing', path
  dfs = readDB(path) 
  for df in dfs:
    assert (len(df))
  for i, df in enumerate(dfs): 
    print i, 'SHAPE:', df.shape
    print 'ROWIDS from :', df.ROWID_x.min(), df.ROWID_x.max()
  df = pd.concat(dfs).drop_duplicates(subset=['day','cname','text']) 
  print '#ROW SUM:', sum([len(_) for _ in dfs])
  print '###RESULT###', df.shape
  print 'ROWIDS from :', df.ROWID_x.min(), df.ROWID_x.max()
  print 'DONE TESTING\n'
  return df


if __name__=='__main__':
  if argv[-1] == 'units':
    testQuery()
    print 'TESTING BAD PATH \n'
    #testRead(BAD_PATH)
    print 'TESTING WITH CHAT_DB\n'
    #testRead(CHAT_DB)
    print 'TESTING WITH MY_MOBILE BACKUP\n'
    testRead(MY_MOBILE_BACKUP)
  else:
    testMSG(argv[-1])
#Test clean on fake DF
