import argparse
import os
import sys

from btlib import cerebero, signals, download


import logging   

logger_name = '.'.join(__file__.replace('.py', '').split('/')[-2:])
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s- %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()    
    argparser.add_argument('--cerebero', help='cerbero', action='store_true') 
    argparser.add_argument('--signals', help='signals', action='store_true')
    argparser.add_argument('--fast-sim', help='Fast Simulation', action='store_true')
    argparser.add_argument('--trigger-download', help='download', action='store_true')
    args = argparser.parse_args()
    logger.info(args)
    if args.cerebero:        
        exit_code = cerebero.main()
        sys.exit(exit_code)
    elif args.signals:        
        exit_code = signals.main()
        sys.exit(exit_code)
    elif args.fast_sim:        
        exit_code = signals.fast_simulation()
        sys.exit(exit_code)        
    elif args.trigger_download:
        exit_code = download.main()
        sys.exit(exit_code)
        
        
        
    