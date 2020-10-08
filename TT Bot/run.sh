#!/bin/sh

virtualenv venv
. venv/bin/activate
pip3 install -r requirements.txt

[ "$1" = "-db" ] && python3 DB.py

python3 Bot.py
