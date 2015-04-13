#!/bin/bash
# install requirements.text
pip install -r requirements.txt
python chat_to_csv.py
open index.html -a Safari
open fig1.png
