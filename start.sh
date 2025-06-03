#!/bin/bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
export FLASK_APP=main.py
python3 main.py
