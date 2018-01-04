#!/usr/bin/env python

from subprocess import call
from multiprocessing import Pool
from functools import partial
import ujson
from .api.BitAPI import BitAPI
from classes.db.RethinkDatabase import Database
from classes.ml.MachineLearning import MachineLearning
from .cextutils.utils import calculate_lastest_low_high, calculate_prices
from .logger import Logger
from .utils import get_time
from .tasks import save_executions


# Keeping this global!
bfx = BitAPI()


def beep():
    call(["play", "-q", "beep.mp3"])


def trader(crypto, usd):
    db = Database()
    try:
        active = crypto['active']
        currency = crypto['symbol']
        # After been loaded from threads we must get the correct value depending on currency
        ticker, trades = db.get_lastest_price(currency), []
        # This is just a precaution to not think that the value change...
        if crypto['last_id'] == ticker['id']:
            Logger.save_logger_file('trader: last_id not equal to ticker id.')
            return
        else:
            crypto['last_id'] = ticker['id']

        # Amount of currency to buy or sell
        amount = crypto['amount']
        # get last price available from bitfinex
        last_price = float(ticker['last_price'])
        low = float(ticker['low'])
        high = float(ticker['high'])

        # Let's get data from table to make better decisions
        _data = db.get_lastest_price_data(currency.upper())

        # Calculate a probable value low and high
        low, high = calculate_lastest_low_high(low, high, _data)

        min_profit = crypto['min_profit']
        max_profit = crypto['max_profit']
        # Calculate values to buy / sell
        c_min, c_min_max, c_max, c_mean = calculate_prices(last_price, min_profit, max_profit, low, high)
        should_buy = db.should_buy(currency, last_price)
        should_sell = db.should_sell(currency, last_price)

        # Only buy or sell if crypto is active
        if active:
            Logger.save_logger_file(f'Last price for {currency}: {last_price} at {get_time()}')
            # BUY
            if c_min < last_price < c_min_max and usd > (last_price * amount):
                Logger.save_logger_file(f'Trying to buy : {currency} for {last_price} : wait number = {crypto["wait_to_buy"]}')
                if crypto['wait_to_buy'] >= 4 and should_buy:  # wait 3 times before buy...
                    Logger.save_logger_file(f'Buying {currency} : {amount} for {last_price} at {get_time()}.')
                    executed = bfx.place_order(f'{amount}', str(last_price), 'buy', 'exchange market', currency)
                    # Limit the min price we can sell our coins...
                    # it prevents for selling for lower prices than what we bought
                    if last_price > crypto["min_price_to_sell"]:
                        Logger.save_logger_file(f'Min price to sell {currency}: {last_price} at {get_time()}')
                        crypto["min_price_to_sell"] = last_price
                    if executed.isdigit():
                        crypto['wait_to_buy'] = 0
                        beep()
                else:
                    crypto['wait_to_buy'] += 1
            # SELL
            elif last_price >= c_max and crypto['available'] > 0 and last_price >= crypto["min_price_to_sell"]:
                Logger.save_logger_file(f'Trying to sell : {currency} for {last_price} : wait number = {crypto["wait_to_sell"]}')
                # wait 2 times before sell to see if the value dont go higher
                if crypto['wait_to_sell'] >= 1 and should_sell:
                    coin_qtd = crypto['available']
                    Logger.save_logger_file(f'Selling {currency} : {coin_qtd} for {last_price}  at {get_time()}.')
                    executed = bfx.place_order(f'{coin_qtd}', str(last_price), 'sell', 'exchange market', currency)
                    if executed.isdigit():
                        crypto['wait_to_sell'] = 0
                        beep()
                else:
                    crypto['wait_to_sell'] += 1
        return {
            'currency': currency,
            'low': low,
            'high': high,
            'price': last_price,
            'c_min': c_min,
            'c_min_max': c_min_max,
            'c_max': c_max,
            'c_mean': c_mean,
            'active': active,
            'wait_to_buy': 0 if crypto['wait_to_buy'] > 10 else crypto['wait_to_buy'],
            'wait_to_sell': 0 if crypto['wait_to_sell'] > 10 else crypto['wait_to_sell'],
            'min_price_to_sell': crypto['min_price_to_sell']
        }
    except Exception as e:
        Logger.save_logger_file(f'Error in trader : {e}')
        return


class BitfinexBot():

    def __init__(self):
        self.db = Database()
        self.ml = MachineLearning()
        self.usd = 0
        with open('config.json', 'r') as handler:
            self.cryptos = ujson.load(handler)

    def main(self, _loop, _data):
        self.refresh(_loop, _data)
        self.trader(_loop, _data)
        self.orders(_loop, _data)
        self.clean(_loop, _data)

    def clean(self, _loop, _data):
        Logger.remove_logger_file()
        # Remove old balances
        self.db.remove_balances()
        # Remove old execution
        self.db.remove_execution()
        # Lets remove old prices values
        for crypto in self.cryptos:
            currency = crypto['symbol']
            self.db.remove_tickers(currency)
        _loop.set_alarm_in(500, self.clean)

    def refresh(self, _loop, _data):
        _loop.draw_screen()
        BitfinexBot.set_message_2_text(_loop, f'')
        # print(bfx.symbols())
        balances = self.get_balaces(_loop, _data)
        if len(balances) > 0:
            updates = [
                ('headers', u'Type  \t '.expandtabs(15)),
                ('headers', u'Currency \t'.expandtabs(15)),
                ('headers', u'Amount  \t '.expandtabs(15)),
                ('headers', u'Available\n'.expandtabs(15))]

            for balance in balances:
                if float(balance["amount"]) > 0 or float(balance["available"]) > 0 or balance['currency'] == 'usd':
                    # Show color for available currency value
                    color = 'white'
                    if float(balance["available"]) > 0:
                        color = 'change '
                    self.__append_text(updates, f'{balance["type"]} \t', tabsize=15)
                    self.__append_text(updates, f' {balance["currency"]} \t', tabsize=15, color='getting quote')
                    self.__append_text(updates, f' {balance["amount"]} \t', tabsize=15)
                    self.__append_text(updates, f'  {balance["available"]} \n', tabsize=15, color=color)
                # Loding information to use in bot
                if balance['currency'] == 'usd':
                    # Saving USD balance information
                    self.db.save_balance(balance)
                    self.usd = float(balance['available'])
                for crypto in self.cryptos:
                    if balance['currency'] == crypto['name']:
                        crypto['available'] = float(balance['available'])
            BitfinexBot.set_balance(_loop, updates)
        BitfinexBot.set_message_1_text(_loop, f'refresh at {get_time()}')
        _loop.set_alarm_in(5, self.refresh)

    def get_balaces(self, _loop, _data):
        balances = []
        try:
            balances = [balance if balance['type'] == 'exchange' else None for balance in bfx.balances()]
            balances = list(filter(None, balances))
        except TypeError as e:
            BitfinexBot.set_message_2_text(_loop, f'Error: {e}...')
        return balances

    def orders(self, _loop, _data):
        _loop.draw_screen()
        orders = bfx.active_orders()
        updates = [
            ('headers', u'Order  \t '.expandtabs(15)),
            ('headers', u'Symbol \t'.expandtabs(15)),
            ('headers', u'Side  \t '.expandtabs(10)),
            ('headers', u'Price  \t'.expandtabs(10)),
            ('headers', u'Amount  \n'.expandtabs(15)),
        ]

        items = []
        for order in orders:
            color = 'change '
            if order["side"] == 'sell':
                color += 'negative'
            self.__append_text(updates, f'{order["id"]} \t', tabsize=15)
            self.__append_text(updates, f' {order["symbol"]} \t', tabsize=15, color='getting quote')
            self.__append_text(updates, f' {order["side"]} \t', tabsize=10, color=color)
            self.__append_text(updates, f'  {order["price"]} \t', tabsize=10)
            self.__append_text(updates, f'  {order["original_amount"]} \n', tabsize=15)

        BitfinexBot.set_orders(_loop, updates)
        BitfinexBot.set_message_1_text(_loop, f'update orders at {get_time()}')
        _loop.set_alarm_in(15, self.orders)

    def trader(self, _loop, _data):
        _loop.draw_screen()
        update_bs = []
        BitfinexBot.set_message_1_text(_loop, f'start update price at {get_time()}')
        with Pool(4) as pool:
            update_bs = list(filter(None, pool.map(partial(trader, usd=self.usd), self.cryptos, chunksize=2)))
            # Update the crypto information came from multiprocess
            for crypto in self.cryptos:
                for ucrypto in update_bs:
                    if ucrypto['currency'].upper() == crypto['symbol'].upper():
                        crypto['wait_to_buy'] = ucrypto['wait_to_buy']
                        crypto['wait_to_sell'] = ucrypto['wait_to_sell']
                        crypto['min_price_to_sell'] = ucrypto['min_price_to_sell']
                        break
        self.update_buy_sell_values(_loop, update_bs)
        save_executions.delay(update_bs)
        BitfinexBot.set_message_1_text(_loop, f'update price at {get_time()}')
        _loop.set_alarm_in(0.75, self.trader)

    def update_buy_sell_values(self, _loop, update_bs):
        updates = [
            ('headers', u'Currency\t '.expandtabs(4)),
            ('headers', u'Low\t'.expandtabs(10)),
            ('headers', u'High\t'.expandtabs(11)),
            ('headers', u'Price\t'.expandtabs(11)),
            ('headers', u'Min\t'.expandtabs(11)),
            ('headers', u'Min +\t'.expandtabs(11)),
            ('headers', u'Max\t'.expandtabs(11)),
            ('headers', u'Mean\t'.expandtabs(10)),
            ('headers', u'Active\n'.expandtabs(5)),
        ]
        for value in update_bs:
            active_color = 'change ' if value["active"] else 'change negative'
            low = value["low"]
            high = value["high"]
            v_low = '{0:.4f}\t'.format(low) if low <= 100 else '{0:.2f}\t'.format(low)
            v_high = '{0:.4f}\t'.format(high) if high <= 100 else '{0:.2f}\t'.format(high)
            self.__append_text(updates, f'{value["currency"]}\t', tabsize=13, color='getting quote')
            self.__append_text(updates, f'{v_low}', tabsize=10)
            self.__append_text(updates, f'{v_high}', tabsize=11)
            self.__append_text(updates, f'{value["price"]}\t', tabsize=11, color='quote')
            self.__append_text(updates, f'{value["c_min"]}\t', tabsize=11, color='change negative')
            self.__append_text(updates, f'{value["c_min_max"]}\t', tabsize=11, color='price')
            self.__append_text(updates, f'{value["c_max"]}\t', tabsize=11, color='change ')
            self.__append_text(updates, f'{value["c_mean"]}\t', tabsize=5)
            self.__append_text(updates, f'{value["active"]}\n', tabsize=5, color=active_color)
        BitfinexBot.set_buysell_text(_loop, updates)

    def update_machine_learning_values(self, _loop, update_ml):
        try:
            updates = [
                ('headers', u'Currency\t '.expandtabs(4)),
                ('headers', u'Bayes\t '.expandtabs(9)),
                ('headers', u'Linear\t'.expandtabs(10)),
                ('headers', u'Ridge\t'.expandtabs(10)),
                ('headers', u'Lasso\n'.expandtabs(9)),
            ]
            for value in update_ml:
                self.__append_text(updates, f'{value["currency"]}\t', tabsize=13, color='getting quote')
                for model in value['models']:
                    color = 'change '
                    v_model = model[0]
                    if value["last_price"] >= v_model:
                        color += 'negative'
                    v_model = '{0:.4f}\t'.format(v_model) if v_model <= 100 else '{0:.2f}\t'.format(v_model)
                    self.__append_text(updates, v_model, tabsize=5, color=color)
                self.__append_text(updates, f'\n', tabsize=1)
            BitfinexBot.set_predictions_text(_loop, updates)
        except TypeError as e:
            BitfinexBot.set_message_2_text(_loop, f'update_machine_learning_values error: {e}...')

    def __append_text(self, l, s, tabsize=10, color='white'):
        l.append((color, s.expandtabs(tabsize)))

    @staticmethod
    def set_balance(_loop, text):
        _loop.widget.contents['body'][0][0].base_widget.set_text(text)

    @staticmethod
    def set_orders(_loop, text):
        _loop.widget.contents['body'][0][1].base_widget.set_text(text)

    @staticmethod
    def set_buysell_text(_loop, text):
        _loop.widget.contents['body'][0][2].base_widget.set_text(text)

    @staticmethod
    def set_predictions_text(_loop, text):
        _loop.widget.contents['body'][0][3].base_widget.set_text(text)

    @staticmethod
    def set_message_1_text(_loop, text):
        _loop.widget.contents['body'][0][4][0].base_widget.set_text(text)

    @staticmethod
    def set_message_2_text(_loop, text):
        _loop.widget.contents['body'][0][4][1].base_widget.set_text(text)
