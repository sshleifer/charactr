import pandas as pd
import datetime as dt


def safe_msg_len(text):
    return len(text) if text else 0


def filter_based_on_col(df, col, bool_func):
    return df.loc[df[col].apply(bool_func)]


def check_saved_data():
    '''Get saved data if it exists.'''
    keep = ['ROWID_x','text','tstamp','chat_id','is_sent','cname']
    return pd.read_csv('msg.csv')[keep] if os.path.exists('msg.csv') else []


def concat_saved_data(msg, saved_data):
    '''Adds saved data to extracted data, if saved data exists.'''
    str2date = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    saved_data['tstamp'] = saved_data.tstamp.apply(str2date)
    if 'msg_len' not in saved_data.columns:
      saved_data['msg_len'] =  saved_data.text.fillna(0).apply(safe_msg_len)
    cutoff = saved_data.tstamp.max()
    return pd.concat([saved_data, msg[msg.tstamp > cutoff]])


