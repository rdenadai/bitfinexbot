#!/usr/bin/env python

import time
import datetime


def get_time():
    timestamp = datetime.datetime.fromtimestamp(time.time())
    return timestamp.strftime("%d-%m-%Y %H:%M:%S")


def get_date():
    timestamp = datetime.datetime.fromtimestamp(time.time())
    return timestamp.strftime("%d-%m-%Y")


def get_hour():
    timestamp = datetime.datetime.fromtimestamp(time.time())
    return timestamp.strftime("%H:%M:%S")


def get_timestamp():
    return time.time()