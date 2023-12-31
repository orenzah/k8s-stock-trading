import datetime
import inspect
import logging
import os
import sys

import requests
from binance.spot import Spot

# create logger
currentdir = os.path.dirname(
    os.path.abspath(
        inspect.getfile(
            inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
format = ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO, format=format)
logger = logging.getLogger("binance.positioner")

# set format


API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
INTERVAL = os.getenv('INTERVAL')
API_URL = os.getenv('API_URL')


def map_symbol(symbol: str):
    match(symbol):
        case "BTCUSDT":
            return "BTC_USDT"


def sell_symbol(shares, symbol):
    pass


def buy_symbol(shares, symbol):
    pass


def get_symbols():
    return ["BTCUSDT"]


def current_positions(client, active_positions):
    for position in active_positions:
        logger.info(f'Position: {position}')
        logger.info(f'Symbol: {position["symbol"]}')
        symbol = position['symbol']
        symbol = symbol.replace('_', '')


def current_positions(client, active_positions):

    for position in active_positions:
        symbol = position['symbol'].replace('_', '')
        klines = client.klines(symbol=symbol, interval="1m")
        # Get the last kline
        kline = klines[-1]
        close_price = float(kline[4])
        # Get the stop lose price
        stop_lose_price = position['stop_lose_price']
        # Get exit price
        exit_price = position['exit_price']
        # compare close price with stop lose and exit price
        # if one of the prices is reached, then close the position
        if close_price <= stop_lose_price or close_price >= exit_price:
            # call function to sell the position in Binance
            # rslt = sell_symbol(position['shares'], symbol)
            # if not rslt:
            #     logger.error(f'Error: {rslt}')
            #     time.sleep(10)
            #     continue
            # send request to the API to close the position
            data = {
                "exit_price": close_price,
                "entry_price": position['entry_price'],
                "shares": position['shares'],
                "symbol": position['symbol'],
                "position_id": position["id"]
            }
            logger.info(f'Closing position: {data}')
            # data = (close_position.entry_price, close_position.close_price, close_position.shares, close_position.symbol, close_position.id)
            resp = requests.post(
                f'http://api:8000/Positions/Close', json=data)
            if resp.status_code != 200:
                logger.error(f'Error: {resp.status_code}')
                # time.sleep(10)
                continue
            continue

        logger.info(f'position entry_datetime {position["entry_datetime"]}')
        entry_timestamp = datetime.datetime.strptime(position['entry_datetime'], '%Y-%m-%dT%H:%M:%S')
        timeout_seconds = datetime.timedelta(seconds=position['timeout_seconds'])
        if entry_timestamp + timeout_seconds <= datetime.datetime.now():
            # expired
            # check if the position is expired
            # if expired, close the position
            data = {
                "exit_price": close_price,
                "entry_price": position['entry_price'],
                "shares": position['shares'],
                "symbol": position['symbol'],
                "position_id": position["id"]
            }
            logger.info(f'Closing position due to timeout: {data}')
            # data = (close_position.entry_price, close_position.close_price, close_position.shares, close_position.symbol, close_position.id)
            resp = requests.post(
                f'http://api:8000/Positions/Close', json=data)
            logger.info(f'Closed position: {position}')


while True:
    try:
        client = Spot(api_key=API_KEY, api_secret=API_SECRET)
        logger.info('Connected to Binance')
        break
    except Exception as e:
        logger.error(f'Exception: {e}')
        # time.sleep(10)
while True:
    # Get from API list of open positions
    resp = requests.get('http://api:8000/Positions/List')
    if resp.status_code != 200:
        logger.error(f'Error: {resp.status_code}')
        # time.sleep(10)
        continue
    positions = resp.json()
    logger.info(f'Positions: {positions}')

    active_positions = []
    for position in positions['positions']:
        if position['active'] == 0:
            continue
        active_positions.append(position)
    logger.info(f'Active positions: {active_positions}')

    # Get account balance and get kline for the symbol
    account = client.account()
    balances = account['balances']
    current_positions(client, active_positions)

    if len(active_positions) < 1:
        # check if there is a buy signal
        # get the list of symbols
        symbols = get_symbols()
        signals = []
        for symbol in symbols:
            data = {
                "symbol": symbol.replace('_', '')
            }
            resp = requests.post(f'http://api:8000/Signals/ShouldEnterPosition', json=data)
            logger.info(f'ShouldEnterPosition: {resp}')
            if resp.status_code != 200:
                logger.error(f'Error: {resp.status_code}')
                # time.sleep(10)
                continue
            signal = resp.json()
            if signal is None:
                continue
            if signal['enter_position'] == "false":
                logger.info(f'No signal to enter position for symbol {symbol}')
                continue
            if signal['enter_position'] == "true":
                signal['symbol'] = symbol
                signals.append(signal)
        if len(signals) == 0:
            logger.info('No signals to enter a new position')
            # time.sleep(10)
            continue
        # signals.sort(key=lambda x: x['confidence'])
        signal = signals[0]
        logger.info(f'Signal: {signal}')

        # call function to buy the symbol in Binance
        shares = 0.1
        # rslt = buy_symbol(shares, symbol) # TODO
        # if not rslt:
        #     logger.error(f'Error: {rslt}')
        #     time.sleep(10)
        #     continue
        # send request to the API to create the position
        klines = client.klines(symbol=symbol, interval="1m")
        # Get the last kline
        kline = klines[-1]
        # Get the close price
        entry_price = close_price = float(kline[4])
        shares = 100 / entry_price
        data = {
            "entry_price": entry_price,
            "exit_price": signal['take_profit'],
            "shares": shares,
            "symbol": map_symbol(symbol),
            "timeout_seconds": signal['timeout_seconds'],
            "stop_lose_price": signal['stop_loss']
        }
        logger.info(f'Creating position: {data}')
        resp = requests.post(
            f'{API_URL}/Positions/Create', json=data)

        if resp.status_code != 200:
            logger.error(f'Error: {resp.status_code}')
            # time.sleep(10)
            continue
        logger.info(f'Created position: {resp.json()}')

    # time.sleep(10)
