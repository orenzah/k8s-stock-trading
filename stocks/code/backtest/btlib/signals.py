import sys
import os
import logging
import datetime
import httpx
import pandas as pd
import asyncio
from datetime import datetime
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from api.routes import signals


PATH = os.path.dirname(os.path.join(os.path.dirname(__file__), '../'))
####
auth = None
if os.environ['USER'] == 'orenzah':
    os.environ['API_URL'] = 'https://api.zahtlv.freeddns.org'
    local_mode = True
    with open(f'{PATH}/api_creds.ignore') as f:
        username = f.readline().strip()
        password = f.readline().strip()
        auth = (username, password)
####    
API_URL = os.environ.get('API_URL', 'http://api:8000')
logger_name = __name__
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s- %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class Simulation:
    def __init__(self, start_date=None, end_date=None, iteration_interval=None, interval=None):
        if start_date is None:
            self.start_date = datetime.datetime(2022, 9, 1, 1, 15, 0)
        if end_date is None:
            self.end_date = datetime.datetime(2023, 9, 2)
        if iteration_interval is None:
            self.iteration_interval = 15 # minutes
        if interval is None:
            self.interval = "1m"
        self.enter_values = []
        self.exit_values = []
        self.aggregate = 0
        

def simulate_position(start_time, end_time, interval, symbol="BTCUSDT", stop_loss=None, take_profit=None):
    json_data = {
        "symbol": symbol,
        "interval": f"{interval}m",
        "start_time": start_time,
        "end_time":  end_time,
        "limit": (end_time - start_time) / (interval * 60 * 1000),
        "kline_type": "spot"
    }   
    logger.debug(f"simulate json_date: {json_data}")  
    response = httpx.post(f'{API_URL}/Stocks/GetCacheHistoricalKline', json=json_data, auth=auth)
    if response.status_code != 200:
        logger.error(response)
        return
    logger.debug(response)
    response_data = response.json()            
    
    df = pd.DataFrame(response_data)
    df['close'] = df['close'].astype(float)
    logger.debug(df.head())
    i = 0                
    for ind in df.index:                        
        value = df['close'][ind]
        i = ind        
        if value <= stop_loss:
            logger.debug("stop_loss")                        
            break
        elif value >= take_profit:
            logger.debug("take_profit")            
            break
    return value, i
    
def simulate_position2(df: pd.DataFrame , stop_loss=None, take_profit=None):
    for ind in df.index:
        value = df['close'][ind]
        i = ind
        if value <= stop_loss:                                
            break
        elif value >= take_profit:            
            break
    return value, i



def fast_simulation():
    start_time = int(datetime(2020, 8, 1).timestamp()) * 1000
    end_time = int(datetime(2023, 9, 14).timestamp()) * 1000
    symbol = "BTCUSDT"
    interval = "1m"
    json_data = {
        "symbol": symbol,
        "interval": interval,
        "start_time": start_time,
        "end_time":  end_time,
        "limit": (end_time - start_time) / (1 * 60 * 1000),
        "kline_type": "spot"
    }
    
    response = httpx.post(f'{API_URL}/Stocks/GetCacheHistoricalKline', json=json_data, auth=auth, timeout=None)
    if response.status_code != 200:
        raise Exception(response)
    response_data = response.json()
    df = pd.DataFrame(response_data)
    df['close'] = df['close'].astype(float)
    jump_future = None
    entry_vals = np.array([])
    exit_vals = np.array([])
    aggregate = 0    
    for entry_datetime in range(start_time + 1000*60*60*24, end_time, 1000*60*15):
        if entry_datetime % (1000*60*60*24*30) == 0:
            date = datetime.fromtimestamp(entry_datetime/1000).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"{date}")
            logger.info(f"Results Aggregated: {aggregate}")
        if jump_future != None and entry_datetime < jump_future:
            continue
        jump_future = None
        # cut a day before entry_datetime
        day_df = df[df['open_time'] < entry_datetime]
        day_df = day_df[day_df['open_time'] > entry_datetime - 1000*60*60*24]
        day_df = day_df.reset_index(drop=True)
        result = signals.bollinger(day_df, entry_datetime)
        if result is None:            
            continue
        else:
            entry_vals = np.append(entry_vals, day_df['close'].iloc[-1])
            next_df = df[df['open_time'] > entry_datetime]
            next_df = next_df[next_df['open_time'] < entry_datetime + result[2]*1000]
            next_df = next_df.reset_index(drop=True)
            value, ind =  simulate_position2(next_df, result[0], result[1])
            jump_future = next_df['open_time'][ind]                
            exit_vals = np.append(exit_vals, value)
            aggregate += (value/day_df['close'].iloc[-1] - 1)
    logger.info(f"Results Aggregated: {aggregate}")
    return None

            
    
        
def get_close_timestamp(dt, symbol="BTCUSDT"):
    json_data = {
        "symbol": symbol,
        "interval": "1m",
        "start_time": dt-60*1000,
        "end_time":  dt,
        "limit": 1,
        "kline_type": "spot"
    }
    logger.debug(f"get close timestamp json_date: {json_data}") 
    response = httpx.post(f'{API_URL}/Stocks/GetCacheHistoricalKline', json=json_data, auth=auth)
    if response.status_code != 200:
        logger.error(response)
        return
    logger.debug(response)
    response_data = response.json()
    return response_data[0]      



def main():
    logger.info('main')
    sim = Simulation()
    # from unix time
    sim.start_date = datetime.datetime.fromtimestamp(1662015600000/1000)
    for start_time in range(int(sim.start_date.timestamp()) * 1000, int(sim.end_date.timestamp()) * 1000, sim.iteration_interval * 60 * 1000):        
        # start_time = int(datetime(2023, 9, 1).timestamp()) * 1000
        # end_time = int(datetime(2023, 9, 2).timestamp()) * 1000
        
        end_time = datetime.datetime.fromtimestamp(start_time / 1000) + datetime.timedelta(days=1)
        end_time = int(end_time.timestamp()) * 1000 
                
        interval_min = int(sim.interval.replace('m', ''))
        
        limit = (end_time - start_time) / (interval_min * 60 * 1000)
                    
        interval = sim.interval
        
        json_data = {
            "symbol": "BTCUSDT",
            "interval": interval,
            "start_time": start_time,
            "end_time":  end_time,
            "limit": limit,
            "kline_type": "spot"
        }
        try:
            response = httpx.post(f'{API_URL}/Stocks/GetCacheHistoricalKline', json=json_data, auth=auth)
        except Exception as e:
            logger.error("Error in request", e)
            return
        if response.status_code != 200:
            logger.error(response)
            return
        
        logger.debug(response)                   
        response_data = response.json()            
        if response_data == None:
            logger.debug("response_data is None")
            return
        
        logger.debug('df = pd.DataFrame(response_data)')
        df = pd.DataFrame(response_data)        
        df['close'] = df['close'].astype(float)
        logger.debug('signal = signals.get_signal')
        query = signals.QueryEnter()
        query.symbol = "BTCUSDT"
        query.entry_datetime = datetime.datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
        current_val = get_close_timestamp(start_time)
        current_close = float(current_val['close'])
        logger.debug(f"current_val: {current_val}")
        signal = asyncio.run(signals.should_enter_position(query, auth=auth))
        logger.debug(f"signal: {signal}")        
        if signal['enter_position'] == 'true':
            sim.enter_values += [current_close]            
            logger.debug(f"signal: {signal}")                        
            value, enter = simulate_position(start_time=end_time, 
                              end_time=(end_time+signal['timeout_seconds']*1000),
                              interval=interval_min, 
                              stop_loss=signal['stop_loss'], 
                              take_profit=signal['take_profit'])
            sim.exit_values += [value]
            
            logger.debug(f"value, enter: {value} {current_close}")
            logger.debug(f"change: {value/current_close}")            
            sim.aggregate += (value/current_close - 1)            
            logger.info(f"Results\n{sim.enter_values}\n{sim.exit_values}\nAggregated: {sim.aggregate}")


    logger.info("Simulation done")            
    logger.info(f"Results\n{sim.enter_values}\n{sim.exit_values}\nAggregated: {sim.aggregate}")