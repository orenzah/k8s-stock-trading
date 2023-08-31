import datetime
import json

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel
import requests
from requests.auth import HTTPBasicAuth

router = APIRouter()

class QueryEnter(BaseModel):
    symbol: str
    entry_datetime: str = None # date format: 2021-01-01 00:00:00       
    
class HistoricalKlineQuery(BaseModel):
    symbol: str = "BTCUSDT"
    interval: str = "1m"
    start_time: int = 0
    end_time: int = 0
    limit: int = 1
    kline_type: str = "spot"

@router.post("/ShouldEnterPosition", tags=["signals"])
def should_enter_position(query: QueryEnter):
    symbol = query.symbol    
    entry_datetime = query.entry_datetime
    if entry_datetime is None:
        entry_datetime = datetime.datetime.now()
    else:
        entry_datetime = datetime.datetime.strptime(entry_datetime, "%Y-%m-%d %H:%M:%S")
    # get last 24 hours pair data
    url = "https://api.zahtlv.freeddns.org/Stocks/GetHistoricalKline"  # Replace with the actual API endpoint
    username = "nir"
    password = "nirDUffnhb4u48Kn8m7"

    payload = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "start_time": entry_datetime.timestamp()*1e3 - 60*60*24*1e3,
        "end_time": entry_datetime.timestamp()*1e3,
        "limit": 60*24,
    }

    response = requests.post(url,data = json.dumps(payload), auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        # select only rows before entry_datetime
        df = df[df["open_time"] < entry_datetime.timestamp()*1e3]
        df["close"] = pd.to_numeric(df["close"])
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["bollinger_upper"] = df["close"].rolling(16).mean() + 1.618 * df["close"].rolling(16).std()
        df["bollinger_lower"] = df["close"].rolling(16).mean() - 1.618 * df["close"].rolling(16).std()
        df = df.dropna()

        print (df.iloc[-1]["close"], df.iloc[-1]["bollinger_lower"], df.iloc[-2]["close"], df.iloc[-2]["bollinger_lower"])
        if df.iloc[-1]["close"] > df.iloc[-1]["bollinger_lower"] and df.iloc[-2]["close"] < df.iloc[-2]["bollinger_lower"]:
            take_profit = (df.iloc[-1]["bollinger_upper"]+df.iloc[-1]["bollinger_lower"])/2
            stop_loss = df.iloc[-1]["close"]-(take_profit-df.iloc[-1]["close"])
            return True, 60, stop_loss, take_profit
        else:
            return False, None, None, None
    # TODO send request to the algo server to get the answer
    # answer is a boolean and timeout_seconds and stop_lose_price and exit_price\
    # default return None    
    return None


if __name__ == "__main__":
    query = QueryEnter(symbol="BTCUSDT")
    start = datetime.datetime.now() - datetime.timedelta(hours=3)
    for minute in range(180):
        query.entry_datetime = (start + datetime.timedelta(minutes=minute)).strftime("%Y-%m-%d %H:%M:%S")
        print(minute/180,should_enter_position(query))
