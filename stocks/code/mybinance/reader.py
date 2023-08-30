import datetime
import os

import influxdb_client
import numpy as np
from binance.spot import Spot
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Load InfluxDB connection parameters from environment variables
influx_host = os.getenv("INFLUX_HOST")
influx_port = int(os.getenv("INFLUX_PORT"))
influx_token = os.getenv("INFLUXDB_TOKEN")
influx_database = os.getenv("INFLUX_DATABASE")
influx_org = os.getenv("INFLUX_ORG")


# parameters for the strategy
# 1. time interval
# 2. symbol
# 3. start date
# 4. end date
# 5. sequence length
# 6. sequence type (up or down)
# 7. sequence size (number of sequences to find)
# 8. sequence size (number of sequences to find)
# 9. sequence size (number of sequences to find)
# 10. sequence size (number of sequences to find)

interval = os.getenv("INTERVAL")
symbol = os.getenv("SYMBOL")


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
account = client.account()
possible_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']
kline = client.klines(symbol='ETHBTC', interval='1m', limit=5)


def class_kline(kline):
    if kline['close'] > kline['open']:
        return 'green'
    elif kline['close'] < kline['open']:
        return 'red'
    else:
        return 'doji'


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

print([class_kline(unpack_kline(k)) for k in kline])
if condition_red.all():
    # buy signal
    # get BTC balance and buy ETH
    for balance in account['balances']:
        if balance['asset'] == 'BTC':
            my_balance = float(balance['free'])
            break
    print(my_balance)
    print('buy')
    # buy ETH with BTC balance with value of 10% of the balance
    params = {
        'symbol': 'ETHBTC',
        'side': 'BUY',
        'type': 'MARKET',
        'quoteOrderQty': np.around(my_balance * 0.1, 3)
    }
    order = client.new_order(**params)
    print(order)

elif condition_green.all():
    for balance in account['balances']:
        if balance['asset'] == 'ETH':
            my_balance = float(balance['free'])
            break
    # sell signal
    print(my_balance)
    print('sell')
    # buy BTC with ETH balance with value of 10% of the balance
    value = unpack_kline(kline[-1])['close']
    params = {
        'symbol': 'ETHBTC',
        'side': 'SELL',
        'type': 'MARKET',
        'quoteOrderQty': np.around(value * my_balance * 0.5, 3)
    }
    order = client.new_order(**params)
    print(order)
