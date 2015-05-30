import pandas as pd

def msgLen(text):
  return len(text) if text else 0

def filterDF(df, col, bool_func):
  df['keep'] = df[col].apply(bool_func)
  return df[df.keep].drop('keep', 1)
