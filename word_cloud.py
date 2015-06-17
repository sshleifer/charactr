### cloud.py

from constants import *

# takes in a msg df and writes its message text to a file
# returns a counter of the words
def writeWords(msg):
  retStr = ''

  text = msg['text'].str.lower()

  for x in text:
    # x = x.decode('unicode_escape').encode('ascii', 'ignore')
    try: 
      words = str(x).split(' ')       # str needed bc some nonstrings in df
      for w in words:
        if w not in stopwords:
          retStr += w.translate(None, punctuation) + ', '
    except UnicodeEncodeError:
      retStr += ''      # do nothing

  retStr = retStr[:-2]                      # deletes extra ', '
  retStr = retStr.translate(None, ':.')     # deletes : and . -- thoughts?
  f = open('word_cloud.txt', 'w')
  f.write(retStr)
