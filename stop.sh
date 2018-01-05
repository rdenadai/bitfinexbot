#!/usr/bin/env bash

sudo killall rethinkdb
sudo killall celery
pkill -9 -f 'python run_btfxwss.py'