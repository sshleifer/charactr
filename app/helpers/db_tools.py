'''These are tools we use to find the right tables to pull from. Code rarely
ends up being called once we find the right table. -SS'''
import fnmatch
import pandas as pd
import sqlite3
###Random Debugging Tools
def find_unis(df):
  unis = {}
  for col in df.columns:
    try:
      unis[col] = len(df[col].unique())
    except TypeError:
      continue
  return unis

def tbl_to_df(tab_name, con):
  query = "SELECT * from " + tab_name
  df = pd.read_sql(query, con)
  return df

def getTabs(cursor):
  '''Assists database navigation.'''
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  return [x[0] for x in cursor.fetchall()]

def allData(cursor):
  '''For exploring DB environment'''
  for table in getTabs(cursor):
    cursor.execute("SELECT * FROM " + table)
    k = cursor.fetchall()
    print table, ': (10 rows)'
    print '**************'
    try:
      print k[:10]
    except IndexError:
      print k

def possDB():
  '''Experimental attempt at finding all .abcddb files in file system.'''
  matches = []
  for root, dirnames, filenames in os.walk('~/Library'):
    for filename in fnmatch.filter(filenames, '*.abcddb'):
      matches.append(os.path.join(root, filename))
  return matches
