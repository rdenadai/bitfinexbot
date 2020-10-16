#!/usr/bin/env python

import time
import uuid
import ujson
from btfxwss import BtfxWss
from classes.tasks import save_ticker, save_trade
from classes.utils import get_time, get_timestamp, get_hour, get_date


if __name__ == "__main__":
    wss = BtfxWss()
    wss.start()

    while not wss.conn.connected.is_set():
        time.sleep(0.5)

    cryptos = []
    with open("config.json", "r") as handler:
        cryptos = ujson.load(handler)

    if cryptos:
        for crypto in cryptos:
            currency = crypto["symbol"].upper()
            # Subscribe to some channels
            wss.subscribe_to_ticker(currency)
            wss.subscribe_to_trades(currency)
            time.sleep(0.5)

        try:
            print("Starting...")
            while True:
                try:
                    for crypto in cryptos:
                        currency = crypto["symbol"].upper()
                        # Accessing data stored in BtfxWss:
                        # get currency ticker information
                        ticker_q = wss.tickers(currency)
                        while not ticker_q.empty():
                            ticker = ticker_q.get()[0][0]
                            save_ticker.delay(
                                {
                                    "uid": str(uuid.uuid4()),
                                    "currency": currency,
                                    "last_price": ticker[6],
                                    "volume": ticker[7],
                                    "bid": ticker[0],
                                    "ask": ticker[2],
                                    "low": ticker[9],
                                    "high": ticker[8],
                                    "bid_size": ticker[1],
                                    "ask_size": ticker[3],
                                    "daily_change": ticker[4],
                                    "daily_change_perc": ticker[5],
                                    "date": get_date(),
                                    "hour": get_hour(),
                                }
                            )
                        # get all trades for this currency
                        # trades_q = wss.trades(currency)
                        # while not trades_q.empty():
                        #     trades = trades_q.get()[0]
                        #     if trades[0] in ['te', 'tu']:
                        #         save_trade.delay({
                        #             'uid': str(uuid.uuid4()),
                        #             'currency': currency,
                        #             'mts': trades[1][1],
                        #             'amount': trades[1][2],
                        #             'price': trades[1][3],
                        #             'date': get_date(),
                        #             'hour': get_hour()
                        #         })
                    time.sleep(0.1)
                except Exception as e:
                    print(e)
        except KeyboardInterrupt as ke:
            print(ke)
            for crypto in cryptos:
                currency = crypto["symbol"].upper()
                # Unsubscribing from channels:
                wss.unsubscribe_from_ticker(currency)
                wss.subscribe_to_trades(currency)
                time.sleep(0.5)
            # Shutting down the client:
            wss.stop()