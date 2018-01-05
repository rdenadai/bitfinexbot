#!/usr/bin/env python

import asyncio
import urwid
import uvloop
from classes.BitfinexBot import BitfinexBot
import numpy


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


if __name__ == '__main__':
    # Ignore warnings!
    numpy.warnings.filterwarnings('ignore')
    bot = BitfinexBot()

    # Tuples of (Key, font color, background color)
    palette = [
        ('titlebar', 'dark red', ''),
        ('refresh button', 'dark green,bold', ''),
        ('quit button', 'dark red', ''),
        ('getting quote', 'dark blue', ''),
        ('quote', 'dark cyan', ''),
        ('price', 'yellow', ''),
        ('headers', 'white,bold', ''),
        ('change ', 'dark green', ''),
        ('change negative', 'dark red', '')]

    # Notice "refresh button" and "quit button" keys were defined above in the color scheme.
    menu = urwid.Text([u'Press (', ('quit button', u'Q'), u') to quit.'])

    header_text = urwid.Text(u' Bitfinex Bot')
    header = urwid.AttrMap(header_text, 'titlebar')

    # BALANCES
    balance_text = urwid.Text(u'')
    balance_filler = urwid.Filler(balance_text, valign='top', top=0, bottom=1)
    balance_padding = urwid.Padding(balance_filler, left=1, right=1)
    balance_box = urwid.LineBox(balance_padding, title='Balances')

    # ORDERS
    quote_text = urwid.Text(u'')
    quote_filler = urwid.Filler(quote_text, valign='top', top=0, bottom=1)
    v_padding = urwid.Padding(quote_filler, left=1, right=1)
    quote_box = urwid.LineBox(v_padding, title='Orders')

    # PREDICT
    pred_text = urwid.Text(u'')
    pred_filler = urwid.Filler(pred_text, valign='top', top=0, bottom=1)
    predv_padding = urwid.Padding(pred_filler, left=1, right=1)
    pred_box = urwid.LineBox(predv_padding, title='Predictions')

    # BUY / SELL
    bs_text = urwid.Text(u'')
    bs_filler = urwid.Filler(bs_text, valign='top', top=0, bottom=1)
    bsv_padding = urwid.Padding(bs_filler, left=1, right=1)
    bs_box = urwid.LineBox(bsv_padding, title='Buy / Sell')

    # MESSAGES
    msg_text = urwid.Text(u'')
    msg_filler = urwid.Filler(msg_text, valign='top', top=0, bottom=1)
    mv_padding = urwid.Padding(msg_filler, left=1, right=1)
    msg2_text = urwid.Text(u'')
    msg2_filler = urwid.Filler(msg2_text, valign='top', top=0, bottom=1)
    mv2_padding = urwid.Padding(msg2_filler, left=1, right=1)
    pile_msg = urwid.Pile([mv_padding, mv2_padding])
    msg_box = urwid.LineBox(pile_msg, title='Messages')

    # INTERFACE
    pile = urwid.Pile([balance_box, quote_box, bs_box, pred_box, msg_box])
    layout = urwid.Frame(header=header, body=pile, footer=menu)

    # uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # start event loop
    evl = urwid.AsyncioEventLoop(loop=asyncio.get_event_loop())
    loop = urwid.MainLoop(layout, palette, unhandled_input=exit_on_q, event_loop=evl)
    loop.set_alarm_in(0, bot.main)
    loop.run()
