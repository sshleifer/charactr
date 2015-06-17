### Takes a name string as a parameter and prints your chat history with that
### person

import pandas as pd
from sys import argv
from chat_to_csv import writeChat

def formPrint(row, last):
  if (row['date_orig'] - last['date_orig']) > 3599:
    print
    print '     ', row['date']

  if row['is_sent'] == 0:
    print row['text']
  else:
    print '                ', row['text']

def writeHistory(person):
  person = person.lower()
  work = writeChat([])
  print work.head(
  # stopped here, concat extra space
  sam = work[work.cname == person]
  hai = pd.DataFrame(sam.text, columns = ['text'])
  hai['date'] = sam.date
  hai['date_orig'] = 5 # sam.date_orig
  hai['is_sent'] = sam.is_sent

  row_iterator = hai.iterrows()
  try:
    _, last = row_iterator.next()
    print '     ', last['date']
    formPrint(last, last)
    for index, row in row_iterator:
      formPrint(row, last)
      last = row
  except StopIteration:
    print person, 'not in address book'

if __name__ == '__main__':
  print argv[-1]
  person = argv[-1]
  writeHistory(person)
