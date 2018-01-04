#!/usr/bin/env python

import time
import datetime


def remove_logger_file():
    with open('log.txt', 'w') as fhandler:
        fhandler.write('')


def save_logger_file(_data):
    timestamp = datetime.datetime.fromtimestamp(time.time())
    with open('log.txt', 'a') as fhandler:
        fhandler.write(f'{_data} : {timestamp.strftime("%d-%m-%Y %H:%M:%S")}\n')
