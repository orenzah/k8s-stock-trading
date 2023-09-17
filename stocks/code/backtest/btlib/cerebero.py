from datetime import datetime
import backtrader as bt
import logging
import os
import httpx
import pandas as pd
from matplotlib import pyplot as plt
PATH = os.path.dirname(os.path.join(os.path.dirname(__file__), '../'))
####
if os.environ['USER'] == 'orenzah':
    os.environ['API_URL'] = 'https://api.zahtlv.freeddns.org'
    local_mode = True
    with open(f'{PATH}/api_creds.ignore') as f:
        username = f.readline().strip()
        password = f.readline().strip()
####    
API_URL = os.environ.get('API_URL', 'http://api:8000')        
# Create a subclass of Strategy to define the indicators and logic
logger_name = __name__
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s- %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=60   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal
        self._accumulate = True

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside                
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position


def main():
    logger.info("main")
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
    start_time = int(datetime(2023, 9, 1).timestamp()) * 1000
    end_time = int(datetime(2023, 9, 2).timestamp()) * 1000
    interval_min = 1
    
    limit = (end_time - start_time) / (interval_min * 60 * 1000)
        
    logger.debug(f"limit: {limit}")
    interval = f"{interval_min}m"
    
    json_data = {
        "symbol": "BTCUSDT",
        "interval": interval,
        "start_time": start_time,
        "end_time":  end_time,
        "limit": limit,
        "kline_type": "spot"
    }    
    response = httpx.post(f'{API_URL}/Stocks/GetHistoricalKline', json=json_data, auth=(username, password))
    response_data = response.json()    
    for item in response_data:
        for k,v in item.items():
            logger.debug(f"{k}: {v}")
        break
        
    # create bt data feed from pandas dataframe
    df = pd.DataFrame(response_data)    
    df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')    
    df.set_index('datetime', inplace=True)
    df.drop(['open_time', 'close_time'], axis=1, inplace=True)    
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df = df.astype(float)
    logger.debug(df.head())
    data = bt.feeds.PandasData(dataname=df)
    
        
    # Create a data feed
    # data = bt.feeds.YahooFinanceData(dataname='MSFT',
    #                                 fromdate=datetime(2011, 1, 1),
    #                                 todate=datetime(2012, 12, 31))
    logger.info(data)
    cerebro.adddata(data)  # Add the data feed

    cerebro.addstrategy(SmaCross)  # Add the trading strategy
    rslt = cerebro.run()
    for r in rslt:
        logger.info(r)    
    cerebro.plot()
    starttime_str = datetime.fromtimestamp(start_time / 1000).strftime('%Y-%m-%d')
    endtime_str = datetime.fromtimestamp(end_time / 1000).strftime('%Y-%m-%d')
    
    logger.info(f"{starttime_str} - {endtime_str}")
    plt.savefig(f'plot.{starttime_str}_{endtime_str}.png')
    return 0