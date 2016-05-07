import pandas as pd
import datetime

def write_parallel_csv(msg):
    msg['days_old'] = pd.to_datetime(msg.tstamp).apply(lambda x: (datetime.datetime.now() - x).days)
    msg['n_chars'] = msg.text.fillna('').apply(len)

    original_cols = ['text', 'cname', 'is_sent', 'n_chars', 'days_old']
    new_cols = ['name', 'group',  'sent?', 'len (chars)', 'days old']
    m2 = msg[original_cols]
    m2.columns = new_cols
    m2.set_index('name').to_csv('csv/parallel.csv', encoding='utf-8')
