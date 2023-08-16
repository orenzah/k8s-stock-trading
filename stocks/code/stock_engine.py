import os
import requests
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


import logging

import json

logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

# create logger
logger = logging.getLogger('simple_example')
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

# Load InfluxDB connection parameters from environment variables
influx_host = os.getenv("INFLUX_HOST")
influx_port = int(os.getenv("INFLUX_PORT"))
influx_token = os.getenv("INFLUXDB_TOKEN")
influx_database = os.getenv("INFLUX_DATABASE")
influx_org = os.getenv("INFLUX_ORG")
logger.info(influx_host)
logger.info(influx_port)
logger.info(influx_token)
logger.info(influx_database)
logger.info(influx_org)

url = f"http://{influx_host}:{influx_port}"

# NASDAQ API endpoint
nasdaq_api_url = "https://api.nasdaq.com/api/screener/stocks"
headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}
# Fetch stock data from NASDAQ API
while True:
    logger.debug('response = requests.get(nasdaq_api_url)')
    response = requests.get(nasdaq_api_url, headers=headers)
    # logger.debug('stock_data = response.json()')
    stock_data = response.json()
    # with open('/venv/stock_data.json', 'r') as example:
    #     stock_data = json.load(example)
    # logger.debug(stock_data)
    # Prepare InfluxDB data
    influx_data = [
        {
            "measurement": "stock",
            "tags": {
                "name": stock["name"],
                "symbol": stock["symbol"]
            },
            "fields": {
                "price": float(stock["lastsale"].replace("$", "").replace(",", "")),
                "symbol": stock["symbol"],
                "name": stock["name"],
                "netchange": float(stock["netchange"].replace(",", "")),
                "pctchange": float(stock["pctchange"].replace("%", "")),
                "marketCap": float(stock["marketCap"].replace(",", "")),
                "url": stock["url"]
            }
        }
        for stock in stock_data["data"]['table']["rows"]
    ]

    # Connect to InfluxDB and write data
    logger.debug('client = InfluxDBClient(url=url, token=influx_token, org=influx_org)')
    logger.debug(url)
    client = InfluxDBClient(url=url, token=influx_token, org=influx_org)
    logger.debug('write_api = client.write_api(write_options=SYNCHRONOUS)')
    bucket = influx_database
    logger.debug('write_api.write(bucket, influx_org, influx_data)')
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # write_api.write(bucket, influx_org, influx_data)
    for data in influx_data:
        logger.debug(data)
        write_api.write(bucket, influx_org, data)
    sleep_time = 60
    logger.info(f'Sleeping for {sleep_time} seconds')
    time.sleep(sleep_time)    



