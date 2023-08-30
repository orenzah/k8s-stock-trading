import inspect
import os
import sys
import time

import requests
from api import sell_symbol
from binance.spot import Spot
from infra.log import get_logger

# create logger
currentdir = os.path.dirname(
    os.path.abspath(
        inspect.getfile(
            inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


logger = get_logger('binance.positioner')

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
INTERVAL = os.getenv('INTERVAL')


def current_positions():
    for position in active_positions:
        symbol = position['symbol']
        # Get kline for the symbol
        klines = client.klines(symbol=symbol, interval="1m")
        # Get the last kline
        kline = klines[-1]
        # Get the close price
        close_price = float(kline[4])
        # Get the stop lose price
        stop_lose_price = position['stop_lose_price']
        # Get exit price
        exit_price = position['exit_price']
        # compare close price with stop lose and exit price
        # if one of the prices is reached, then close the position
        if close_price <= stop_lose_price or close_price >= exit_price:
            # call function to sell the position in Binance
            rslt = sell_symbol(position['shares'], symbol)
            if not rslt:
                logger.error(f'Error: {rslt}')
                time.sleep(10)
                continue
            # send request to the API to close the position
            resp = requests.get(
                f'http://api:8000/Positions/Close/{position["id"]}')
            if resp.status_code != 200:
                logger.error(f'Error: {resp.status_code}')
                time.sleep(10)
                continue

        logger.info(f'Closed position: {position}')
        continue


while True:
    try:
        client = Spot(key=API_KEY, secret=API_SECRET)
        logger.info('Connected to Binance')
        break
    except Exception as e:
        logger.error(f'Exception: {e}')
        time.sleep(10)
while True:
    # Get from API list of open positions
    resp = requests.get('http://api:8000/Positions/List')
    if resp.status_code != 200:
        logger.error(f'Error: {resp.status_code}')
        time.sleep(10)
        continue
    positions = resp.json()
    logger.info(f'Positions: {positions}')

    active_positions = []
    for position in positions:
        if position['active'] == 0:
            continue
        active_positions.append(position)
    logger.info(f'Active positions: {active_positions}')

    # Get account balance and get kline for the symbol
    account = client.account()
    logger.info(f'Account: {account}')
    balances = account['balances']
    logger.info(f'Balances: {balances}')
    current_positions()

    if len(active_positions) < 1:
        # check if there is a buy signal
        # get the list of symbols
        pass

    time.sleep(10)
