import datetime
import json
import logging
import os
import sys

import httpx
import pandas as pd
import requests
from fastapi import APIRouter
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from signals.bollinger import bollinger

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.propagate = False

API_URL = os.getenv("API_URL")


class QueryEnter(BaseModel):
    symbol: str = "BTCUSDT"
    entry_datetime: str = None  # date format: 2021-01-01 00:00:00
    algorithm: str = "bollinger"


class HistoricalKlineQuery(BaseModel):
    symbol: str = "BTCUSDT"
    interval: str = "1m"
    start_time: int = 0
    end_time: int = 0
    limit: int = 1
    kline_type: str = "spot"


def get_signal(end_time: int, symbol: str = "BTCUSDT", df: pd.DataFrame = None):
    # select only rows before entry_datetime
    df = df[df["open_time"] < end_time]
    df["close"] = pd.to_numeric(df["close"])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["bollinger_upper"] = df["close"].rolling(16).mean() + 1.618 * df["close"].rolling(16).std()
    df["bollinger_lower"] = df["close"].rolling(16).mean() - 1.618 * df["close"].rolling(16).std()
    df = df.dropna()

    # print(df.iloc[-1]["close"], df.iloc[-1]["bollinger_lower"], df.iloc[-2]["close"],
    #       df.iloc[-2]["bollinger_lower"])
    # logger.debug(df.iloc[-1]["close"], df.iloc[-1]["bollinger_lower"], df.iloc[-2]["close"],
    #                df.iloc[-2]["bollinger_lower"])
    possible_take_profit = (df.iloc[-1]["bollinger_upper"] + df.iloc[-1]["bollinger_lower"]) / 2
    possible_stop_loss = df.iloc[-1]["close"] - (possible_take_profit - df.iloc[-1]["close"])
    logger.debug(f"possible_take_profit: {possible_take_profit}")
    logger.debug(f"possible_stop_loss: {possible_stop_loss}")
    if df.iloc[-1]["close"] > df.iloc[-1]["bollinger_lower"] and df.iloc[-2]["close"] < df.iloc[-2]["bollinger_lower"]:
        take_profit = (df.iloc[-1]["bollinger_upper"] + df.iloc[-1]["bollinger_lower"]) / 2
        stop_loss = df.iloc[-1]["close"] - (take_profit - df.iloc[-1]["close"])
        ret_val = {
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "timeout_seconds": 60 * 60,
            "enter_position": "true"
        }
        return ret_val
    else:
        return {"enter_position": "false"}


@router.post("/ShouldEnterPosition", tags=["signals"])
async def should_enter_position(query: QueryEnter, auth=None):

    logger.info("ShouldEnterPosition")
    logger.debug(query)

    symbol = query.symbol
    entry_datetime = query.entry_datetime
    if entry_datetime is None:
        entry_datetime = datetime.datetime.now()
    else:
        # from unix time
        entry_datetime = datetime.datetime.strptime(entry_datetime, "%Y-%m-%d %H:%M:%S")

    #############################

    # get last 24 hours pair data
    url = f"{API_URL}/Stocks/GetCacheHistoricalKline"  # Replace with the actual API endpoint

    payload = {
        "symbol": symbol,
        "interval": "1m",
        # 1 day before entry_datetime
        "start_time": int((entry_datetime - datetime.timedelta(days=1)).timestamp()) * 1e3,
        "end_time": int(entry_datetime.timestamp() * 1e3),
        "limit": 60 * 24,
    }
    logger.debug(payload)
    logger.debug(entry_datetime.timestamp() * 1e3)
    logger.debug(entry_datetime)

    async with httpx.AsyncClient() as client:
        logger.debug("Sending request")
        
        response = await client.post(url, data=json.dumps(payload), auth=auth)
        logger.debug(response)
    # response = requests.post(url, data=json.dumps(payload), auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            
            df = pd.DataFrame(response.json())
            match query.algorithm:
                case "bollinger":
                    result = bollinger(df, entry_datetime.timestamp() * 1e3)
                case _:
                    result = None                        
            if result is None:
                return {"enter_position": "false"}
            else:
                return {
                    "take_profit": result[0],
                    "stop_loss": result[1],
                    "timeout_seconds": result[2],
                    "enter_position": "true"
                }            
    return None
