from binance.spot import Spot
import os
import datetime

import time


import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


import numpy as np

# create logger
import logging

application_name = os.path.basename(__file__)
application_name = application_name.replace('.py', '')
category = os.getenv('CATEGORY')
pod_name = os.getenv('POD_NAME')

logger = logging.getLogger(f'{category}-{pod_name}-{application_name}')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

logger.info('Started')


API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Load InfluxDB connection parameters from environment variables
influx_host = os.getenv("INFLUX_HOST")
influx_port = int(os.getenv("INFLUX_PORT"))
influx_token = os.getenv("INFLUXDB_TOKEN")
influx_database = os.getenv("INFLUX_DATABASE")
influx_org = os.getenv("INFLUX_ORG")




interval = os.getenv("INTERVAL")
if not interval:
    interval = '1m'
SLEEPING_TIME = int(os.getenv("SLEEPING_TIME"))
if not SLEEPING_TIME:
    SLEEPING_TIME = 60









client = Spot(api_key=API_KEY, api_secret=API_SECRET)
influx_client = InfluxDBClient(url=f"http://{influx_host}:{influx_port}", token=influx_token)


def unpack_kline(kline):
    return {
        'open_time': datetime.datetime.fromtimestamp(kline[0] / 1000),
        'open': float(kline[1]),
        'high': float(kline[2]),
        'low': float(kline[3]),
        'close': float(kline[4]),
        'volume': float(kline[5]),
        'close_time': datetime.datetime.fromtimestamp(kline[6] / 1000),
        'quote_asset_volume': float(kline[7]),
        'number_of_trades': int(kline[8]),
        'taker_buy_base_asset_volume': float(kline[9]),
        'taker_buy_quote_asset_volume': float(kline[10]),
        'ignore': float(kline[11]),
    }
def query_data(symbol, start_date, end_date, interval):
    query_api = influx_client.query_api()
    query = f'from(bucket:"{influx_database}")\
        |> range(start: {start_date}, stop: {end_date})\
        |> filter(fn: (r) => r._measurement == "price")\
        |> filter(fn: (r) => r.symbol == "{symbol}")\
        |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)\
        |> yield(name: "mean")'
    tables = query_api.query(query=query, org=influx_org)
    return tables
    



# condition_lt = diffs < 0
# condition_gt = diffs > 0


# # Find the indices where the condition is met
# matching_indices = np.where(condition)[0]

# # Initialize a variable to keep track of found sequences
# found_sequences = []

# # Define the sequence length
# sequence_length = 4

# Iterate through the matching indices to find continuous sequences
# for i in range(len(matching_indices) - sequence_length + 1):
#     if np.all(np.diff(matching_indices[i:i+sequence_length]) == 1):
#         found_sequences.append(diffs[matching_indices[i:i+sequence_length]])
# print(found_sequences)

def class_kline(kline):
    if kline['close'] > kline['open']:
        return 'green'
    elif kline['close'] < kline['open']:
        return 'red'
    else:
        return 'doji'

possible_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']

while True:
    backoff = False
    logger.info(f'Iteration started')
    account = client.account()

    kline = client.klines(symbol='ETHBTC', interval=interval, limit=5)
    
    another_kline = client.klines(symbol='ETHBTC', interval='5m', limit=2)
    another_kline = [unpack_kline(k) for k in another_kline]
    if class_kline(another_kline[0]) == 'green' and class_kline(another_kline[1]) == 'doji':
        # buy ETH with BTC
        if another_kline[1]['close'] >= 1.0/(15.3):
            logger.info(f'Buying BTC with ETH')    
            # get BTC balance and buy ETH    
            for balance in account['balances']:
                if balance['asset'] == 'ETH':
                    my_balance = float(balance['free'])
                    break    
            # sell signal
            logger.info(f'Selling ETH with ETH balance with value of 10% of the balance {np.around(my_balance * 0.1, 3)}')
            
            # buy BTC with ETH balance with value of 10% of the balance
            value = another_kline[1]['close']       
            params = {
                'symbol': 'ETHBTC',        
                'side': 'SELL',
                'type': 'MARKET',        
                'quoteOrderQty': np.around(value * my_balance * 0.75, 3)
            }    
            backoff = True
            logger.debug(params)
            order = client.new_order(**params)
            logger.debug(order)
            
            SLEEPING_TIME = SLEEPING_TIME * 5
            jump_sleeping_time = 10
            for t in range(int(SLEEPING_TIME/jump_sleeping_time)):
                logger.info(f'Left time for {SLEEPING_TIME - t*jump_sleeping_time} seconds')
                time.sleep(jump_sleeping_time)    
            continue



    


    condition_red = np.array([])
    condition_green = np.array([])
    for k in kline:
        k = unpack_kline(k)        
        if class_kline(k) == 'green':
            condition_green = np.append(condition_green, True)
            condition_red = np.append(condition_red, False)
        elif class_kline(k) == 'red':
            condition_red = np.append(condition_red, True)
            condition_green = np.append(condition_green, False)
        else:
            condition_red = np.append(condition_red, False)
            condition_green = np.append(condition_green, False)

    logger.debug([class_kline(unpack_kline(k)) for k in kline])
    if condition_red.all():
        # buy signal
        # get BTC balance and buy ETH    
        for balance in account['balances']:
            if balance['asset'] == 'BTC':
                my_balance = float(balance['free'])
                break    
        logger.debug(my_balance)
        logger.info(f'Buying ETH with BTC balance with value of 10% of the balance {np.around(my_balance * 0.1, 3)}')
        # buy ETH with BTC balance with value of 10% of the balance
        params = {
            'symbol': 'ETHBTC',        
            'side': 'BUY',
            'type': 'MARKET',        
            'quoteOrderQty': np.around(my_balance * 0.1, 3)
        }
        backoff = True 
        logger.debug(params)   
        order = client.new_order(**params)
        logger.debug(order)
        
    elif condition_green.all():
        for balance in account['balances']:
            if balance['asset'] == 'ETH':
                my_balance = float(balance['free'])
                break    
        # sell signal
        logger.info(f'Selling ETH with ETH balance with value of 10% of the balance {np.around(my_balance * 0.1, 3)}')
        
        # buy BTC with ETH balance with value of 10% of the balance
        value = unpack_kline(kline[-1])['close']        
        params = {
            'symbol': 'ETHBTC',        
            'side': 'SELL',
            'type': 'MARKET',        
            'quoteOrderQty': np.around(value * my_balance * 0.5, 3)
        }    
        backoff = True
        logger.debug(params)
        order = client.new_order(**params)
        logger.debug(order)
    
    if backoff:
        SLEEPING_TIME = SLEEPING_TIME * 5
    jump_sleeping_time = 10
    for t in range(int(SLEEPING_TIME/jump_sleeping_time)):
        logger.info(f'Left time for {SLEEPING_TIME - t*jump_sleeping_time} seconds')
        time.sleep(jump_sleeping_time)    





    



