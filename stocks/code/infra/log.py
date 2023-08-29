# this is the logger module to be used by any other module
import logging
import os
from datetime import datetime
import sys




def get_logger(logger_name: str):
    # create logger
    application_name = os.path.basename(__file__)
    application_name = application_name.replace('.py', '')
    parent_folder = os.path.basename(os.path.dirname(__file__))
    logger = logging.getLogger(f'{logger_name}')
    logger.setLevel(logging.DEBUG)

    # set format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # use the format
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
