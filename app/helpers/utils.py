import pandas as pd

def msgLen(text):
  return len(text) if text else 0

def filterDF(df, col, bool_func):
  df['keep'] = df[col].apply(bool_func)
  return df[df.keep].drop('keep', 1)

def checkSavedData():
  '''Get saved data if it exists.''' 
  keep = ['ROWID_x','text','tstamp','chat_id','is_sent','cname']
  return pd.read_csv('msg.csv')[keep] if os.path.exists('msg.csv') else []

def concatSaved(msg, saved_data):
  '''Adds saved data to extracted data, if saved data exists.'''
  str2date = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
  saved_data['tstamp'] = saved_data.tstamp.apply(str2date) 
  if 'msg_len' not in saved_data.columns:
    saved_data['msg_len'] =  saved_data.text.fillna(0).apply(msgLen)
  cutoff = saved_data.tstamp.max()
  return pd.concat([saved_data, msg[msg.tstamp > cutoff]])


