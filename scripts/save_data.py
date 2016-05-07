import pandas as pd
from chat_to_csv import writeChat, checkSavedData
saved_data = checkSavedData()
msg = writeChat(saved_data) #Read in, clean a dataframe of all messages
msg.to_csv('msg.csv', encoding = 'utf-8')
print '''Saved your data at msg.csv \nTry $ head -10 msg.csv to see the file or $ cat msg.csv | wc to see its length.'''

