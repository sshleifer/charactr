#!/bin/bash
if [ "$installed" != "done" ]
then
  pip install -r requirements.txt
  echo "DONE INSTALLING."
  echo "If problems, try $ pip install -r requirements.txt"
fi
export installed="done"
python chat_to_csv.py
open index.html -a Safari
open fig1.png
