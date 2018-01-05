#!/usr/bin/env python

from celery import Celery
from .db.RethinkDatabase import Database


app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task
def save_ticker(_ticker):
    db = Database()
    db.save_ticker(_ticker)


@app.task
def save_trade(_trade):
    db = Database()
    db.save_trade(_trade)


@app.task
def save_executions(_executions):
    db = Database()
    db.save_executions(_executions)