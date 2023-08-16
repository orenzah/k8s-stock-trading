from binance.spot import Spot
import os, time
import datetime

import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


import logging

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


client = Spot(api_key=API_KEY, api_secret=API_SECRET)
influx_client = InfluxDBClient(url=f"http://{influx_host}:{influx_port}", token=influx_token)
exchange_info =  client.exchange_info()
possible_assets = ['DOGE', 'BTC', 'BUSD', 'ETH']
if os.getenv('ASSETS_FILE'):
    with open(os.getenv('ASSETS_FILE'), 'r') as assets_file:
        possible_assets = assets_file.read().splitlines()


    possible_tickers = []
    for asset in possible_assets:
        for sub_asset in possible_assets:        
            if asset != sub_asset:            
                symbol = filter(lambda x: x['symbol'] == asset+sub_asset, exchange_info['symbols'])            
                if list(symbol):                
                    possible_tickers.append(asset+sub_asset)                
                else:
                    symbol = filter(lambda x: x['symbol'] == sub_asset+asset, exchange_info['symbols'])
                    if list(symbol):                    
                        possible_tickers.append(sub_asset+asset)                    
                    else:
                        print('No symbol found for', asset, sub_asset)
                    
write_api = influx_client.write_api(write_options=SYNCHRONOUS)                        
while True:
    for symbol in possible_tickers:    
        ticker = client.ticker_price(symbol=symbol)
        logger.info(symbol, ticker)        
        logger.info(f'{ticker["symbol"]} {ticker["price"]}')
        point = Point("price") \
            .tag("symbol", ticker['symbol']) \
            .field("price", float(ticker['price'])) \
            .time(datetime.datetime.utcnow(), WritePrecision.NS)        
        write_api.write(bucket=influx_database, org=influx_org, record=point)
    time.sleep(sleeping_time)

        

    
    





