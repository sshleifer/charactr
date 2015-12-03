import pandas as pd
import json
import collections as cl
from random import randint
from constants import stopwords

# takes in a msg df and writes json object to word_tree.txt
def bubbleJson(msg):
  retStr = ''

  sent = []
  received = []

  count = cl.Counter()

  text = msg['text'].str.lower()
  is_sent = msg['is_sent']
  cname = msg['cname']

  for i in range(0, len(text)):
    try:
      for w in str(text.iloc[i]).split():
        if w not in stopwords:
          count[w] += 1

      if is_sent.iloc[i] == 0:    # received
        received.append(cname.iloc[i].upper() + ': ' + str(text.iloc[i]))
      else:                       # sent
        sent.append('YOU: ' + str(text.iloc[i]))
    except UnicodeEncodeError:
      continue

  n_words = 30
  top_n_words = sorted(count, key=count.get, reverse=True)[:n_words]
  top_words_dict_list = []

  for w in top_n_words:
    temp_obj = {}
    temp_obj["name"] = w
    temp_obj["re"] = '\\b(' + w + ')\\b'
    temp_obj["x"] = randint(0, 970)
    temp_obj["y"] = randint(0, 640)
    top_words_dict_list.append(temp_obj)

  output = json.dumps({'sent': sent, 'received': received, 'top_words':
                       top_words_dict_list}, sort_keys=True,
                   indent=4, separators=(',', ': '))

  f = open('bubble.txt', 'w')
  f.write(output)
  f.close



msg = pd.read_csv('../csv/msg.csv')
bubbleJson(msg)
