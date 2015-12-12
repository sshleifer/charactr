import pandas as pd

#takes in msg df and writes to parallel.csv
def parallel_csv(msg):
  new_df = pd.DataFrame(msg.text)
  new_df['contact'] = msg.cname
  new_df['is_sent'] = msg.is_sent
  # new_df['length (chars)'] = 
  # new_df['length (words)'] = 
  new_df.to_csv('parallel.csv')
  

msg = pd.read_csv('../csv/msg.csv')
parallel_csv(msg)
