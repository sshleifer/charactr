'''Reads in some tables from chat.db, joins and cleans them,
and then calls contacts.py to label phone numbers with contact names.'''
import datetime as dt
import os
import pandas as pd
import sqlite3
from sys import argv

from app.contacts import addresses, groupbyContact
from app.word_cloud import writeWords
from app.helpers.utils import filterDF, msgLen, checkSavedData, concatSaved
from app.parallel import write_parallel_csv
from app.time_chart import timePanel

CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")
BASENAME_ON_MOST_MACHINES = '3d0d7e5fb2ce288813306e4d4636395e047a3d28'
MOBILE_BASE = os.path.expanduser('~/Library/Application Support/MobileSync/Backup/')
DATE_OFFSET_THAT_SOMEHOW_WORKS = 978307200
#for magic date offset, see https://stackoverflow.com/questions/10746562/parsing-date-field-of-iphone-sms-file-from-backup


def date_converter(apple_offset_dt):
    try:
        # some users have 9 extra digits on their timestamps, like shleifer
        date_int = int(str(apple_offset_dt)[:9])
        return dt.datetime.fromtimestamp(date_int + DATE_OFFSET_THAT_SOMEHOW_WORKS)
    except Exception:
        return dt.datetime.fromtimestamp(apple_offset_dt + DATE_OFFSET_THAT_SOMEHOW_WORKS)


def make_dataframe_from_db_files(db_path):
    '''Writes message number,type. text, other person and date to msg, a df'''
    try:
        db = sqlite3.connect(db_path)
        msg_raw = pd.read_sql("SELECT * from message", db)
        chat = pd.read_sql("SELECT * from chat", db)
        cmj = pd.read_sql("SELECT * from chat_message_join", db)
        hdl = pd.read_sql("SELECT * from handle", db)
    except Exception:
        print 'Non-Fatal db error at {}\n'.format(db_path)
        return []
    ### Merge db reads
    full_chat = chat.merge(cmj, left_on='ROWID', right_on='chat_id', how='inner')
    msg = msg_raw.merge(full_chat, left_on='ROWID', right_on='message_id')
    msg = msg.merge(hdl, left_on='handle_id', right_on='ROWID')
    ### Find contact names and clean columns

    #date_cut = lambda x: dt.datetime.fromtimestamp(x + DATE_OFFSET_THAT_SOMEHOW_WORKS)
    msg['tstamp'] = msg.date.apply(date_converter)
    msg['day'] = msg.tstamp.apply(lambda x: x.date())
    msg['msg_len'] = msg.text.fillna('').apply(msgLen)
    return msg


def query_all_possible_sources(test_path=None):
    '''Reads text data from all possible iPhone backups.
        Falls back on iMessage (which is smaller).'''
    backups = [make_dataframe_from_db_files(os.path.join(x[0], BASENAME_ON_MOST_MACHINES))
               for x in os.walk(MOBILE_BASE)
               if BASENAME_ON_MOST_MACHINES in x[2]]
    if not backups:
        print 'Could not find iPhone backup'
    if test_path is not None:
        backups.append(make_dataframe_from_db_files(test_path))
    backups.append(make_dataframe_from_db_files(CHAT_DB))
    return filter(lambda x: len(x) > 0, backups)

SAVE_DIR = 'csv/'
def concat_and_deduplicate_history(saved_data=[]):
    '''combine and deduplicate the various db reads'''
    msg = pd.concat(query_all_possible_sources()).drop_duplicates(subset=['day', 'chat_identifier', 'text'])
    clist = addresses(msg)
    def findName(cid):
        cid = cid.replace('+1','')
        try:
            return clist[cid].rstrip()
        except KeyError:
            return cid.rstrip()
    msg['cname'] = msg.chat_identifier.apply(findName)
    return concatSaved(msg,saved_data) if saved_data else msg


def try_df_to_csv(df, path):
    try:
        df.to_csv(path, encoding='utf-8')
    except Exception as e:
        print 'ERROR on CSV WRITE to %s:', e, df % (path)


def create_csvs(hidegroups=True, use_saved=False, n_best=10):
    '''Create the relevant csvs'''
    print "being executed at", os.path.abspath('.')
    saved_data = checkSavedData() if use_saved else []
    msg = concat_and_deduplicate_history(saved_data)
    print msg.shape
    if len(argv) <= 1 or hidegroups:
        msg = filterDF(msg, 'cname', lambda x: not x.startswith('chat'))
    ppl = groupbyContact(msg.copy()).sort_values('totlen', ascending=False)
    print ppl.head()
    besties = map(lambda x: x.rstrip(), ppl.index[:n_best])
    print 'besties:', besties
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)
    ts = timePanel(msg, besties)  # is this still needed?
    keep_cols = ['text','tstamp','is_sent','cname']

    try_df_to_csv(msg[keep_cols], SAVE_DIR + 'msg.csv')
    try_df_to_csv(ts, SAVE_DIR + 'ts.csv')
    try_df_to_csv(ppl, SAVE_DIR + 'ppl.csv')
    # write_parallel_csv(msg[keep_cols])
    writeWords(msg) # create word_cloud.txt
    result_message = 'Found {} texts in {} conversations from {} to {}'.format(
        len(msg), msg.cname.nunique(), msg.tstamp.min(), msg.tstamp.max()
    )
    print result_message
    return msg  # for interactive use


if __name__ == '__main__':
    create_csvs()
