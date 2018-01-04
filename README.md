# BitfinexBot

Python bot for the [Bitfinex](https://www.Bitfinex.com/) exchange.

## Install

#### Install rethinkdb

```sh
$ echo "deb http://download.rethinkdb.com/apt xenial main" | sudo tee /etc/apt/sources.list.d/rethinkdb.list
$ wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -
$ sudo apt-get update
$ sudo apt-get install rethinkdb
```

#### Install redis

```sh
$ sudo apt-get install redis-server
```

#### Install bot
> This bot needs python3.5+ to work, so be sure you have the right version, if not download [pyenv](https://github.com/pyenv/pyenv) and follow the bellow steps. 

```sh
$ pip install -r requirements.txt
```

## Keys

Create file ```keys.txt``` in the main directory with the following syntax:

    public key
    private key
    [insert newline here]


## Config file

Edit the **config.json** file to add new currencies or change the percentage of profit.
- name: "iot",
- symbol: "iotusd",
- amount: 10,
- min_profit: 0.0055,
- max_profit: 0.0085,
- active: false

DO NOT CHANGE OTHER FIELDS!!

> The symbol field you could find those names from bitfinex api, but in practice is the sort name of the coin and usd. btcusd and etc...


## Run

To run the system you need to execute the following commands:

```sh
$ rethinkdb --bind all
$ celery -A classes.tasks worker --loglevel=info
$ python run_btfxwss.py
$ python run.py
```

Keep in mind, the each command must be executed in their own shell window... the one with bot logic is run.py.

## Compiling the Min, Min+ and Max calculus

If you need to change the calculus made by cextutils, please run the bellow command inside classes/cextutils.
It will recompile python code to C... trying to speed up some calculation.

```sh
$ python setup.py build_ext --inplace
``` 

## DISCLAIMER

This code, if run is your responsability, **i will take no part in it**... if money is lost its up to you.
**I take no responsability for your actions**... so please, don't use this... it is solely for my personal use.
It is here on github just as a **demonstration porpuse... its functional... but its a serious stuff!!!**