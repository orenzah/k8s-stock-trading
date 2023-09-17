import sys
import os
import logging
import datetime
import httpx
import pandas as pd
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
            self.iteration_interval = 1440 # minutes
        if interval is None:
            self.interval = "1m"     
    

def main():    
    sim = Simulation()    
    # logger.debug(f"start_time: {start_time}")
    # start_time = int(datetime(2023, 9, 1).timestamp()) * 1000
    # end_time = int(datetime(2023, 9, 2).timestamp()) * 1000
    
    # end_time = datetime.datetime.fromtimestamp(start_time / 1000) + datetime.timedelta(days=1)
    # end_time = int(end_time.timestamp()) * 1000 
    real_start_time = 1518064800000
    failed = []    
    for start_time in range(real_start_time, 1675300500000, 1000 * 60 * 1000):                
        interval_min = int(sim.interval.replace('m', ''))
        end_time = start_time + (1000 * 60 * 1000)
        limit = (end_time - start_time) / (interval_min * 60 * 1000)
                    
        interval = sim.interval
        
        json_data = {
            "symbol": "BTCUSDT",
            "interval": interval,
            "start_time": start_time,
            "end_time":  end_time,
            "limit": int(limit),
            "kline_type": "spot"
        }
        logger.debug(json_data)
        now = datetime.datetime.now()
        try:
            response = httpx.post(f'{API_URL}/Stocks/FillHistoricalKline', json=json_data, auth=auth, timeout=None)
            after = datetime.datetime.now()
            response_data = response.json()
            logger.debug(f"response time: {after - now}")
            logger.debug(response_data)
        except:
            logger.debug(f"failed: {json_data}")
            failed += [json_data]

    final_failed = []
    for fail in failed:
        logger.debug(f"try again: {fail}")
        try:
            response = httpx.post(f'{API_URL}/Stocks/FillHistoricalKline', json=json_data, auth=auth, timeout=None)
        except:
            logger.debug(f"failed: {json_data}")
            finally_failed += [json_data['start_time']]
    logger.debug(f"final_failed: {final_failed}")
            
        
    