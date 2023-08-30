
# import logging
import datetime
import logging
import os

import influxdb_client
import mysql.connector
import requests
from binance.spot import Spot
from fastapi import APIRouter
from fastapi.logger import logging
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import BaseModel

router = APIRouter()


# Load InfluxDB connection parameters from environment variables
influx_host = os.getenv("INFLUX_HOST")
influx_port = int(os.getenv("INFLUX_PORT"))
influx_token = os.getenv("INFLUXDB_TOKEN")
influx_database = os.getenv("INFLUX_DATABASE")
influx_org = os.getenv("INFLUX_ORG")

influx_client = InfluxDBClient(url=f"http://{influx_host}:{influx_port}", token=influx_token)


class BTPosition(BaseModel):
    symbol: str = "BTCUSDT"
    entry_time: datetime.datetime = datetime.datetime.now() - datetime.timedelta(hours=1)
    entry_price: float = 0.0
    exit_time: datetime.datetime = datetime.datetime.now()
    stop_loss_price: float = 0.0
    timeout_seconds: int = 0
    exit_price: float = 0.0


class BTExchange(BaseModel):
    symbol: str = "BTCUSDT"
    entry_time: datetime.datetime = datetime.datetime.now() - datetime.timedelta(hours=1)


@router.get("/Exchange", tags=["backtesting"])
def get_exchange(exchange: BTExchange):
    symbol = exchange.symbol.replace('_', '')
    entry_time = exchange.entry_time
    # entry_time = entry_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    start = entry_time - datetime.timedelta(seconds=1)
    end = entry_time + datetime.timedelta(seconds=1)
    start = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    end = end.strftime('%Y-%m-%dT%H:%M:%SZ')
    query = f"""from(bucket: {influx_database})
    |> range(start: {start}, stop: {end})
    |> first()
    """
    logger.info(query)
    result = influx_client.query_api().query(org=influx_org, query=query)
    logger.info(result)
    return result
