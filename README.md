# charactr
A standalone desktop app that allows Mac/iMessage users to visualize their
texting history.

##Quick Install (for noobs):
1. Click one of the .zip files above, and download it by clicking the 'Raw'
   Button. 
(Later versions will be slightly cooler, and slightly less likely to work)
2. Unzip the file.
3. Right click and open on the charactr application.
4. This should open localhost:8000 in your browser, with the scatterplot
   showing. (if you have a previous version, you may need to refresh)
5. Hover over dots to see the contacts and their stats.
6. When you are bored, force quit charactr.

If something breaks, take a screenshot of your Mac's console, and post it as an
Issue.

##Instructions for Developers (from terminal):
- $ git clone **this repo**
- $ cd imsg_stats
- $ python imsg_stats.py

The data read from ~/Library/Messages/chat.db.
Data will be written to imsg_stats/ppl.csv, feel free to play
with it, send pull requests. If you add msg.to_csv('msg.csv') to the bottom of chat_to_csv.py, every text will be sent to a csv. If something breaks, take a screenshot of your Mac's console, and post it as an Issue.

##Future Plans

- Support Group Chats
- More Plots, tables
- CrossFilter
- NLP, word clouds
