import pandas as pd
import json

# takes in a msg df and writes json object to word_tree.txt
def treeJson(msg):
  retStr = ''

  sent = []
  received = []

  text = msg['text'].str.lower()
  is_sent = msg['is_sent']

  for i in range(0, len(text) / 100):
    try:
      if is_sent.iloc[i] == 0:    # received
        received.append(str(text.iloc[i]).split())
      else:
        sent.append(str(text.iloc[i]).split())
    except UnicodeEncodeError:
      continue

  output = json.dumps({'sent': sent, 'received': received}, sort_keys=True,
                   indent=4, separators=(',', ': '))

  f = open('word_tree.txt', 'w')
  f.write(output)
  f.close

msg = pd.read_csv('../csv/msg.csv')
treeJson(msg)
