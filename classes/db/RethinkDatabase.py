#!/usr/bin/env python

from datetime import datetime
import rethinkdb as r


class Database():

    def __init__(self):
        self.db_name = 'bitfinex'
        r.connect("localhost", 28015).repl()
        databases = r.db_list().run()
        if self.db_name not in databases:
            r.db_create(self.db_name).run()

        indexes = ['currency', 'timestamp']
        database_tables = r.db(self.db_name).table_list().run()
        tables = ['balance', 'orders', 'tickers', 'trades', 'run_exec']
        for table in tables:
            if table not in database_tables:
                r.db(self.db_name).table_create(table).run()
            # indexes
            indexes_tables = r.db(self.db_name).table(table).index_list().run()
            for index in indexes:
                if index not in indexes_tables:
                    if r.db(self.db_name).table(table).has_fields(index):
                        r.db(self.db_name).table(table).index_create(index).run()

    def save_balance(self, balance):
        balance['timestamp'] = r.expr(datetime.now(r.make_timezone('-03:00')))
        r.db(self.db_name).table('balance').insert(balance).run()

    def save_ticker(self, ticker):
        ticker['timestamp'] = r.expr(datetime.now(r.make_timezone('-03:00')))
        r.db(self.db_name).table('tickers').insert(ticker).run()

    def save_trade(self, trade):
        trade['timestamp'] = r.expr(datetime.now(r.make_timezone('-03:00')))
        r.db(self.db_name).table('trades').insert(trade).run()

    def save_execution(self, exec):
        exec['timestamp'] = r.expr(datetime.now(r.make_timezone('-03:00')))
        r.db(self.db_name).table('run_exec').insert(exec).run()

    def save_executions(self, executions):
        for exec in executions:
            exec['timestamp'] = r.expr(datetime.now(r.make_timezone('-03:00')))
            r.db(self.db_name).table('run_exec').insert(exec).run()

    def remove_execution(self):
        total = r.db(self.db_name).table('run_exec').count().run()
        if total > 50:
            try:
                r.\
                    db(self.db_name). \
                    table('run_exec'). \
                    order_by('timestamp'). \
                    limit(total - 30).\
                    delete().run()
            except Exception as e:
                pass

    def remove_balances(self):
        total = r.db(self.db_name).table('balance').count().run()
        if total > 50:
            try:
                r.\
                    db(self.db_name). \
                    table('balance'). \
                    order_by('timestamp'). \
                    limit(total - 30).\
                    delete().run()
            except Exception as e:
                pass

    def remove_tickers(self, currency):
        total = r.\
            db(self.db_name).\
            table('tickers').\
            filter({'currency': currency.upper()}).\
            count().run()
        if total > 50:
            try:
                r.\
                    db(self.db_name).\
                    table('tickers'). \
                    order_by('timestamp'). \
                    filter({'currency': currency.upper()}). \
                    limit(total - 150).delete().run()
            except Exception as e:
                pass

    def get_lastest_price(self, currency):
        try:
            return r.\
                db(self.db_name).\
                table('tickers'). \
                order_by('timestamp'). \
                filter({'currency': currency.upper()}).\
                nth(-1).run()
        except Exception as e:
            return None

    def should_buy(self, currency, last_price):
        should_buy = set()
        prices = r.\
            db('bitfinex').\
            table('tickers'). \
            order_by(r.desc('timestamp')). \
            filter({'currency': currency.upper()}).\
            limit(3).run()
        for price in prices:
            if last_price <= price['last_price']:
                should_buy.add(True)
            else:
                should_buy.add(False)
        return all(el for el in should_buy)

    def should_sell(self, currency, last_price):
        should_sell = set()
        prices = r.\
            db('bitfinex').\
            table('tickers'). \
            order_by(r.desc('timestamp')). \
            filter({'currency': currency.upper()}).\
            limit(3).run()
        for price in prices:
            if last_price >= price['last_price']:
                should_sell.add(True)
            else:
                should_sell.add(False)
        return all(el for el in should_sell)

    def get_lastest_price_data(self, currency):
        prices = r.\
            db('bitfinex').\
            table('tickers'). \
            order_by(r.desc('timestamp')). \
            filter({'currency': currency.upper()}).\
            limit(75).run()
        x, y, last_price, pred = [], [], 0.0, []
        xapp, yapp = x.append, y.append
        for price in prices:
            predict = [
                price['last_price'],
                price['volume'],
                price['bid'],
                price['ask'],
                price['low'],
                price['high'],
                price['bid_size'],
                price['ask_size'],
                price['daily_change'],
                price['daily_change_perc']
            ]
            # validate trades
            # trds = vals[9]
            # mean_price = 0.0
            # mean_amount = 0.0
            # mean_type = 0.0
            # for trd in trds:
            #     mean_price += float(trd['price'])
            #     mean_amount += float(trd['amount'])
            #     mean_type += 1 if trd['type'] == 'buy' else 0
            # predict.append(mean_price / 100)
            # predict.append(mean_amount / 100)
            # predict.append(mean_type / 100)
            # Join everything inside a simple array
            xapp(predict)
            yapp(price['last_price'])

        if len(y) > 0 and len(x) > 0:
            last_price = y[-1]
            pred = x[-1]
        return x, y, last_price, pred