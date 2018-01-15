# charactr
Mac/iMessage users can interactively visualize their
texting history, using pandas, [d3.js] (http://d3js.org/) and [crossfilter.js](http://square.github.io/crossfilter/).

You must have a mac with iMessage installed. It may also work without iMessage but with an itunes backup.

## From command line:
- $ `git clone git@github.com:sshleifer/imsg_stats.git`
- $ `cd imsg_stats`
- $ `export PYTHONPATH=PYTHONPATH:"."`
- $ `python app/run.py` to see the charts (you may need to adjust your path)
- If that failed, try $ `pip install -r requirements.txt`



The data are read from `~/Library/Messages/chat.db` (and some other paths) by the `read_db()` function in `chat_to_csv.py`
Cleaned data are written to `imsg_stats/csv/`
Then some javascript runs that looks for the cleaned data and makes some pretty visualizations
Help and feature requests welcome and sorely needed!


## Desktop app  (broken, help fix!)
1. Download charactr [Here] (http://pjdewire.github.io/charactr_site/).
2. Right click and open on the charactr application.
3. This should open `localhost:8000` in your browser, with the scatterplot
   showing. If you have a previous version or another application running on port 8000, you will need to kill the other application and refresh.
4. Once you see the scatterplot, read the instructions.
5. Follow links to charts 2 and 3.
5. When you are bored, force quit charactr.

If something breaks, take a screenshot of your Mac and/or browser console, and post it as an
issue or email to sshleifer at gmail dot com.


## Saving Your Data (without viewing charts)
- $ `git clone` **this repo**
- $ `python scripts/save_data.py`
- $ data will be written to `imsg_stats/msg.csv`


# Privacy
- we dont have a server. No data leaves your local machine!

## Future Plans
- Delete unused code
- Support Group Chats
- More Plots, tables
- NLP, word clouds
