# import logging
import os

import mysql.connector
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.logger import logging
from binance.spot import Spot


API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

router = APIRouter()
client = Spot(api_key=API_KEY, api_secret=API_SECRET)

class KlineQuery(BaseModel):
    symbol: str = "BTC_USDT"
    interval: str = "1m"
    limit: int = 1
    

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


