# charactr
A standalone desktop app that allows Mac/iMessage users to visualize their
texting history.

##Quick Install:
1. Download charactr at http://pjdewire.github.io/charactr_site/
2. Right click and open on the charactr application.
3. This should open localhost:8000 in your browser, with the scatterplot
   showing. (if you have a previous version, you may need to refresh)
4. Hover over dots to see the contacts and their stats.
5. Continue to charts 2 and 3.
5. When you are bored, force quit charactr.

If something breaks, take a screenshot of your Mac's console, and post it as an
issue or email to sshleifer@gmail.com.

##Instructions for Developers (from terminal):
- $ git clone **this repo**
- $ cd imsg_stats
- $ python imsg_stats.py

The data read from ~/Library/Messages/chat.db.
Data will be written to `imsg_stats/ppl.csv`and `imsg_stats/msg.csv`. 
Feel free to play with your data and send pull requests. 
If something breaks, take a screenshot of your Mac's console, and post it as an issue.

##Saving Your Data (without viewing charts)
- $ git clone **this repo**
- $ python save_data.py
- $ data will be written to msg.csv

##Future Plans

- Support Group Chats
- More Plots, tables
- NLP, word clouds
