import logging
import os
import time

import influxdb_client
from binance.spot import Spot
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# create logger
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

# Load Binance API key and secret from environment variables
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Load InfluxDB connection parameters from environment variables
influx_host = os.getenv("INFLUX_HOST")
influx_port = int(os.getenv("INFLUX_PORT"))
influx_token = os.getenv("INFLUXDB_TOKEN")
influx_database = os.getenv("INFLUX_DATABASE")
influx_org = os.getenv("INFLUX_ORG")


# Load Sleeping time
sleeping_time = int(os.getenv("SLEEPING_TIME"))


client = Spot()

possible_assets = ['DOGE', 'BTC', 'BUSD']
if os.getenv('ASSETS_FILE'):
    with open(os.getenv('ASSETS_FILE'), 'r') as assets_file:
        possible_assets = assets_file.read().splitlines()

# # API key/secret are required for user data endpoints
binance_client = Spot(api_key=API_KEY, api_secret=API_SECRET)
influx_client = InfluxDBClient(url=f"http://{influx_host}:{influx_port}", token=influx_token)


exchange_list = ['ETCBTC', 'DOGEBTC', 'BTCBTC']

while True:
    logger.info("Reading balance")
    sum_balance = 0  # sum of all balances in BTC
    account = binance_client.account()
    for balance in account['balances']:
        if balance['asset'] in possible_assets:
            logger.info(f"Asset: {balance['asset']}, Free: {balance['free']}, Locked: {balance['locked']}")
            match balance['asset']:
                case 'DOGE':
                    doge_balance = float(balance['free']) * float(client.ticker_price(symbol='DOGEBTC')['price'])
                    sum_balance += doge_balance
                case 'BTC':
                    btc_balance = float(balance['free'])
                    sum_balance += btc_balance
                case 'ETH':
                    eth_balance = float(balance['free']) * float(client.ticker_price(symbol='ETHBTC')['price'])
                    sum_balance += eth_balance
            point = Point("balance").tag("asset", balance['asset']).field("balance", float(balance['free']))
            write_api = influx_client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=influx_database, org=influx_org, record=point)
    # write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    # point = Point("balance").tag("asset", "DOGE").field("balance", doge_balance)
    # write_api.write(bucket=influx_database, org=influx_org, record=point)
    # point = Point("balance").tag("asset", "BTC").field("balance", btc_balance)
    # write_api.write(bucket=influx_database, org=influx_org, record=point)
    # point = Point("balance").tag("asset", "BUSD").field("balance", busd_balance)
    # write_api.write(bucket=influx_database, org=influx_org, record=point)
    # logger.info(f"Sleeping for {sleeping_time} seconds")
    # sum all balances by exchange asset
    point = Point("balance").tag("asset", 'total').field("balance", float(sum_balance))
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=influx_database, org=influx_org, record=point)
    logger.info(f"Total Assets, Free: {sum_balance}")
    time.sleep(sleeping_time)
