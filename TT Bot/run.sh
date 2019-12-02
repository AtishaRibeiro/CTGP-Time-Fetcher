#!/bin/bash

virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt

if [ "$1" = "-db" ]; then
    python3 DB.py
fi

python3 Bot.py
