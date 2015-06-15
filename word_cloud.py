### cloud.py

import collections

# takes in a msg df and writes its message text to a file
# returns a counter of the words
def writeWords(msg):
  retStr = ''
  c = collections.Counter()

  text = msg['text'].str.lower()

  for x in text:
    words = str(x).split(' ')       # str needed bc some nonstrings in df
    c.update(words)
    for w in words:
      retStr += w + ', '

  retStr = retStr[:-2]                      # deletes extra ', '
  retStr = retStr.translate(None, ':.')     # deletes : and . -- thoughts?
  f = open('word_cloud.txt', 'w')
  f.write(retStr)
  
  return c
