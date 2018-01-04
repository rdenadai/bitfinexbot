#!/usr/bin/env python

import requests
import json
import base64
import hmac
import hashlib
import time
import functools


class BitAPI:
    """
        For reference and to make a valid code, im using code developed by dawsbot.
        Check his repo: https://github.com/dawsbot/bitfinex
    """

    def __init__(self):
        self.url = "https://api.bitfinex.com/v1"
        self.keys_file = 'keys.txt'
        self.__read_keys()

    @functools.lru_cache(maxsize=None)
    def __read_keys(self):
        with open(self.keys_file) as fp:
            self.api_key = fp.readline().rstrip()  # put your API public key here.
            self.api_secret = fp.readline().rstrip()  # put your API private key here.

    def __gen_nonce(self):  # generates a nonce, used for authentication.
        return str(int(time.time() * 1000000))

    def __payload_packer(self, payload):  # packs and signs the payload of the request.
        j = bytearray(json.dumps(payload), 'iso-8859-1')
        data = bytes(base64.standard_b64encode(j))

        h = hmac.new(bytearray(self.api_secret, 'iso-8859-1'), data, hashlib.sha384)
        signature = h.hexdigest()

        return {
            "X-BFX-APIKEY": self.api_key,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data
        }

    def ticker(self, symbol='btcusd'):  # gets the innermost bid and asks and information on the most recent trade.
        r = requests.get(f"{self.url}/pubticker/" + symbol, verify=True)  # <== UPDATED TO LATEST VERSION OF BFX!
        rep = r.json()
        try:
            rep['last_price']
        except KeyError:
            return rep['error']
        return rep

    def stats(self, symbol='btcusd'):  # Various statistics about the requested pairs.
        r = requests.get(f"{self.url}/stats/" + symbol, verify=True)  # <== UPDATED TO LATEST VERSION OF BFX!
        return r.json()

    def symbols(self):  # get a list of valid symbol IDs.
        r = requests.get(f"{self.url}/symbols", verify=True)
        rep = r.json()
        return rep

    # authenticated methods

    def active_orders(self):  # view your active orders.
        payload = {
            "request": "/v1/orders",
            "nonce": self.__gen_nonce()
        }

        signed_payload = self.__payload_packer(payload)
        r = requests.post(f"{self.url}/orders", headers=signed_payload, verify=True)
        return r.json()

    def place_order(self, amount, price, side, ord_type, symbol='btcusd', exchange='bitfinex'):  # submit a new order.
        payload = {
            "request": "/v1/order/new",
            "nonce": self.__gen_nonce(),
            "symbol": symbol,
            "amount": amount,
            "price": price,
            "exchange": exchange,
            "side": side,
            "type": ord_type
        }

        signed_payload = self.__payload_packer(payload)
        r = requests.post(f"{self.url}/order/new", headers=signed_payload, verify=True)
        rep = r.json()
        try:
            rep['order_id']
        except KeyError as e:
            print(rep)
            return rep['message']
        return rep

    def delete_order(self, order_id):  # cancel an order.
        payload = {
            "request": "/v1/order/cancel",
            "nonce": self.__gen_nonce(),
            "order_id": order_id
        }

        signed_payload = self.__payload_packer(payload)
        r = requests.post(f"{self.url}/order/cancel", headers=signed_payload, verify=True)
        rep = r.json()

        try:
            rep['avg_execution_price']
        except KeyError as e:
            return rep['error']
        return rep

    def delete_all_order(self):  # cancel an order.
        payload = {
            "request": "/v1/order/cancel/all",
            "nonce": self.__gen_nonce(),
        }

        signed_payload = self.__payload_packer(payload)
        r = requests.post(f"{self.url}/order/cancel/all", headers=signed_payload, verify=True)
        return r.json()

    def balances(self): # see your balances.
        payload = {
            "request": "/v1/balances",
            "nonce": self.__gen_nonce()
        }

        signed_payload = self.__payload_packer(payload)
        r = requests.post(f"{self.url}/balances", headers=signed_payload, verify=True)
        return r.json()
