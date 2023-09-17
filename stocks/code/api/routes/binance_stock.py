# import logging
import datetime
import os
import sys


from binance.spot import Spot
from fastapi import APIRouter
from fastapi.logger import logging
from pydantic import BaseModel

import httpx
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infra.mysql import MySQLConnection

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


# Load InfluxDB connection parameters from environment variables
influx_host = os.getenv("INFLUX_HOST")
influx_port = int(os.getenv("INFLUX_PORT"))
influx_token = os.getenv("INFLUXDB_TOKEN")
influx_database = os.getenv("INFLUX_BUCKET_BINANCE")
influx_org = os.getenv("INFLUX_ORG")


API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

router = APIRouter()
client = Spot(api_key=API_KEY, api_secret=API_SECRET)

mysql_client = MySQLConnection()


class KlineQuery(BaseModel):
    symbol: str = "BTC_USDT"
    interval: str = "1m"
    limit: int = 1


class HistoricalKlineQuery(BaseModel):
    symbol: str = "BTCUSDT"
    interval: str = "1m"
    start_time: int = 0
    end_time: int = 0
    limit: int = 1
    kline_type: str = "spot"



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.propagate = False



# kline = client.klines(symbol='ETHBTC', interval=interval, limit=5)
def unpack_kline(kline):
    return {
        "open_time": kline[0],
        "open": kline[1],
        "high": kline[2],
        "low": kline[3],
        "close": kline[4],
        "volume": kline[5],
        "close_time": kline[6],
        "quote_asset_volume": kline[7],
        "number_of_trades": kline[8],
        "taker_buy_base_asset_volume": kline[9],
        "taker_buy_quote_asset_volume": kline[10],
        "ignore": kline[11]
    }


@router.post("/GetKline", tags=["stocks"])
async def GetKline(query: KlineQuery):
    symbol = query.symbol.replace('_', '')
    interval = query.interval
    if interval not in ['1m', '3m', '5m', '15m', '30m']:
        return None
    limit = query.limit
    klines = client.klines(symbol=symbol, interval=interval, limit=limit)

    ret_val = [unpack_kline(kline) for kline in klines]
    return ret_val


@router.post("/GetHistoricalKline", tags=["stocks"])
async def GetHistoricalKline(query: HistoricalKlineQuery):
    # 2023-09-09 09:59:42,345 - routes.binance_stock - DEBUG 
    # symbol='BTCUSDT' 
    # interval='1m' 
    # start_time=1693526400000 
    # end_time=1693612800000 
    # limit=1 kline_type='spot'

    
    
    logger.debug(query)
    symbol = query.symbol.replace('_', '')
    interval = query.interval
    if interval not in ['1m', '3m', '5m', '15m', '30m', '1d', '1h']:
        return None
    start_time = query.start_time
    if start_time == 0:
        start_time = datetime.datetime.now().timestamp() * 1000
    end_time = query.end_time
    if end_time == 0:
        end_time = datetime.datetime.now().timestamp() * 1000
    if start_time > end_time:
        return None
    limit = query.limit
    limits = []    
    while limit > 1000:
        limits.append(1000)
        limit -= 1000
    limits.append(limit)
    # kline_type = query.kline_type
    kline_type = "spot"
    klines = []
    if 'm' in interval:
        interval_min = int(interval.replace('m', ''))
        interval_min = interval_min * 60 * 1000
    elif 'h' in interval:
        interval_min = int(interval.replace('h', ''))
        interval_min = interval_min * 60 * 60 * 1000
    elif 'd' in interval:
        interval_min = int(interval.replace('d', ''))
        interval_min = interval_min * 24 * 60 * 60 * 1000
    
    for i in range(len(limits)):
        start_time += i * interval_min * 1000
        klines += client.klines(symbol=symbol, interval=interval, limit=limits[i], startTime=start_time, endTime=end_time)

    ret_val = [unpack_kline(kline) for kline in klines]
    return ret_val


def flux_table_to_json_array(tables: list):
    data = [None] * len(tables[0].records)
    for table in tables:                
        for i in range(len(table.records)):
            d = data[i]
            if d is None:
                d = {}
                data[i] = d
            record = table.records[i]            
            match  record.get_field():                
                case "close":
                    d["close"] = record.get_value()
                    d["close_time"] = int(record.get_time().timestamp() * 1000)
                    d["open_time"] = int(record.get_time().timestamp() * 1000 - 59 * 1000)
                case "open":
                    d["open"] = record.get_value()
                    
                case "high":
                    d["high"] = record.get_value()
                    
                case "low":
                    d["low"] = record.get_value()
                    
                case "volume":
                    d["volume"] = record.get_value()
                    
                case "close_time":
                    d["close_time"] = record.get_value()
                    
                case "quote_asset_volume":
                    d["quote_asset_volume"] = record.get_value()
                    
                case "number_of_trades":
                    d["number_of_trades"] = record.get_value()
                    
                case "taker_buy_base_asset_volume":
                    d["taker_buy_base_asset_volume"] = record.get_value()
                    
                case "taker_buy_quote_asset_volume":
                    d["taker_buy_quote_asset_volume"] = record.get_value()  
                         
                case _:
                    logger.debug(f'Unknown field: {record.get_field()}')
    return data
        
                    
                    
    

@router.post("/FillHistoricalKline", tags=["stocks"])
async def FillHistoricalKline(query: HistoricalKlineQuery):    
    client = InfluxDBClient(url=f"http://{influx_host}:{influx_port}", token=influx_token, org=influx_org)    
    payload = {
    "symbol": query.symbol,
    "interval": "1m",
    "start_time": query.start_time,
    "end_time": query.end_time,
    "limit": query.limit,
    "kline_type": query.kline_type
    }
    async with httpx.AsyncClient() as httpx_client:
        logger.debug(f"query to GetHistoricalKline with {payload}")
        query_influx_time = datetime.datetime.now().timestamp() * 1000
        response = await httpx_client.post("http://api:8000/Stocks/GetHistoricalKline", data=json.dumps(payload), timeout=None)                
        logger.debug(f'query httpx time: {datetime.datetime.now().timestamp() * 1000 - query_influx_time}')
        logger.debug(response)
        if response.status_code != 200:
            logger.error(f'Error: {response.status_code}')
            return None
        if response.json() == None:
            logger.error(f'Error: {response.json()}')
            return None
        
        new_data = response.json()            
        logger.debug(f"Data Length is {len(new_data)}")
        # add new data to influxdb        
        write_api = client.write_api(write_options=SYNCHRONOUS)
        query_influx_time = datetime.datetime.now().timestamp() * 1000
        rows = []
        points = []
        for kline in new_data:
            influxdb_datetime_format = datetime.datetime.fromtimestamp(kline['close_time'] / 1000).strftime('%Y-%m-%dT%H:%M:%SZ')                
            data_point = {
                "measurement": "kline",
                "tags": {
                    "symbol": query.symbol,
                    "interval": "1m",                                                
                },
                "time": influxdb_datetime_format,                    
                "fields": {
                    "open": float(kline['open']),
                    "high": float(kline['high']),
                    "low": float(kline['low']),
                    "close": float(kline['close']),
                    "volume": float(kline['volume']),
                    "quote_asset_volume": float(kline['quote_asset_volume']),
                    "number_of_trades": int(kline['number_of_trades']),
                    "taker_buy_base_asset_volume": float(kline['taker_buy_base_asset_volume']),
                    "taker_buy_quote_asset_volume": float(kline['taker_buy_quote_asset_volume']),                        
                }
                
                
            }
            points += [data_point]
            def mysql_datetime_fmt(dt):
                dt = datetime.datetime.fromtimestamp(dt/1000)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
                
            columns = [
                        "symbol", "open_time", "open",
                        "high", "low", "close", "volume", "close_time",
                        "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"
                        ]
            
            data = [
                    query.symbol, mysql_datetime_fmt(kline['open_time']), kline['open'], 
                    kline['high'], kline['low'], kline['close'], kline['volume'], mysql_datetime_fmt(kline['close_time']),
                    kline['quote_asset_volume'], kline['number_of_trades'], kline['taker_buy_base_asset_volume'], kline['taker_buy_quote_asset_volume']
                    ]
            rows += [data]
        mysql_client.insert_rows("kline_data", columns=columns, values=rows)                           
        write_api.write(bucket=influx_database, org=influx_org, record=points)    
        logger.debug(f'query influxdb time: {datetime.datetime.now().timestamp() * 1000 - query_influx_time}')    




@router.post("/GetCacheHistoricalKline", tags=["stocks"])
async def GetCacheHistoricalKline(query: HistoricalKlineQuery):
    first_start = datetime.datetime.now().timestamp() * 1000
    # check query is ok    
    if query.end_time == 0:
        query.end_time = datetime.datetime.now().timestamp() * 1000
        if query.start_time == 0:
            query.start_time = datetime.datetime.now().timestamp() * 1000
    elif query.start_time == 0:
        query.start_time = query.end_time
        limit = 1
                        
    if query.start_time > query.end_time:
        return None
    
    if query.end_time > query.start_time:
        limit = int((query.end_time - query.start_time) / 1000 / 60)
        
        
    
    
    
    # query from MySQL
    open_time_sql = f"FROM_UNIXTIME({query.start_time / 1000})"
    close_time_sql = f"FROM_UNIXTIME({query.end_time / 1000})"
    conditions = [
        "`symbol`='BTCUSDT'",
        "AND"
        f"`open_time`", "BETWEEN", open_time_sql, "AND", close_time_sql
    ]
    where = " ".join(conditions)
    
    # calcualte query time
    now = datetime.datetime.now().timestamp() * 1000
    rslt = mysql_client.select("kline_data",where=where)
    logger.debug(f"query mysql time: {datetime.datetime.now().timestamp() * 1000 - now}")
    cols = mysql_client.show_columns("kline_data")
    
    row_headers = [col[0] for col in cols]
    
    # check expected data exists
    if rslt == None:
        return None
        
    # if expeted data doesn't exist
    if len(rslt) < limit:
        #   send the query to Fill the missing data
        logger.debug(f"Expected data length is {limit} but actual data length is {len(rslt)}")
        query.limit = limit
        logger.debug(rslt[-1])
        
        query.start_time = dict(zip(row_headers, rslt[-1]))['close_time'].timestamp() * 1000
        await FillHistoricalKline(query)
        # re-query from MySQL
        rslt = mysql_client.select("kline_data",where=where)        
    


    results = [   
                dict(zip(row_headers, result)) for
                result in rslt 
                ]        
    for result in results:
        result['open_time'] = int(result['open_time'].timestamp() * 1000)
        result['close_time'] = int(result['close_time'].timestamp() * 1000)
        result['number_of_trades'] = int(result['number_of_trades'])
        for key in result.keys():
            if key != 'open_time' and key != 'close_time' and key != 'number_of_trades':                                
                result[key] = str(result[key])    
    
    # return results
    logger.debug(f"total query time: {datetime.datetime.now().timestamp() * 1000 - first_start}")    
    return results