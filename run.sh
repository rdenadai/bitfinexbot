#!/bin/bash

source venv/bin/activate

sudo killall rethinkdb
sudo killall celery
pkill -9 -f 'python run_btfxwss.py'

nohup sudo rethinkdb --bind all --http-port 8282
nohup celery -A classes.tasks worker --concurrency=10 --loglevel=info --logfile=./logs/celeryd.log &
nohup python run_btfxwss.py &