# charactr
A standalone desktop app that allows Mac/iMessage users to interactively visualize their
texting history, using [d3.js] (http://d3js.org/) and [crossfilter.js](http://square.github.io/crossfilter/)

##Quick Install:
1. Download charactr [Here] (http://pjdewire.github.io/charactr_site/).
2. Right click and open on the charactr application.
3. This should open `localhost:8000` in your browser, with the scatterplot
   showing. If you have a previous version or another application running on port 8000, you will need to kill the other application and refresh.
4. Once you see the scatterplot, read the instructions.
5. Follow links to charts 2 and 3.
5. When you are bored, force quit charactr.

If something breaks, take a screenshot of your Mac and/or browser console, and post it as an
issue or email to sshleifer@gmail.com.

##Instructions for Developers (from terminal):
- $ `git clone` **this repo**
- $ `cd imsg_stats`
- $ `python imsg_stats.py` to see the charts

The data are read from `~/Library/Messages/chat.db` by the `read_db()` function in `chat_to_csv.py`

Cleaned data are written to `imsg_stats/ppl.csv`and `imsg_stats/msg.csv`.
`scatter2.coffee`, `streamgraph.js` and `chart3.js` render Charts 1,2 and 3 respectively.


Play with your data and send pull requests!


##Saving Your Data (without viewing charts)
- $ `git clone` **this repo**
- $ `python save_data.py`
- $ data will be written to `imsg_stats/msg.csv`

##Future Plans

- Support Group Chats
- More Plots, tables
- NLP, word clouds
