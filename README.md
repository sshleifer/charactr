# iMessage Stats
Calculate statistics from backup data stored by iMessage for OS X.

The data is stored by the iMessage app at ~/Library/Messages/chat.db.

###Instructions (from terminal):
- $git clone **this repo**
- $cd imsg_stats
- $pip install -r requirements.txt
- $python chat_to_csv.py
- Data will be in msg.csv and ppl.csv, Histogram will be in fig1.png
- To see hoverable D3 plot: open imsg_stats/index.html in Firefox or Safari
  ($open -a Safari).

###TODO

- Group Chats
- More Plots
- CrossFilter
- NLP
