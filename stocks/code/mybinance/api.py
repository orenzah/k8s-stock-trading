# Binance API
import inspect
import os
import sys

from infra.log import get_logger

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

logger = get_logger('binance.api')


def sell_symbol(shares: float, symbol: str):
    logger.info(f'Selling {shares} of {symbol}')
    params = {
        'symbol': symbol,
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': shares
    }
    try:
        order = client.new_order(**params)
    except Exception as e:
        logger.error(f'Exception: {e}')
        return False
    logger.info(order)
    return True


if __name__ == '__main__':
    print('Binance API')

    logger.info('Binance API')
