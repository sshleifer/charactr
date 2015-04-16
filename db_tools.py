'''These are tools we use to find the right tables to pull from. Code rarely
ends up being called once we find the right table. -SS'''
import fnmatch
import pandas as pd
import sqlite3

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
