import logging
import logging.config

LOGGING_CONFIG = {
    "version":1,
    "root":{
        "handlers" : ["console"],
        "level": "DEBUG"
    },
    "handlers":{
        "console":{
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        }
    },
    "formatters":{
        "std_out": {
            "format": '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            "datefmt":"%d-%m-%Y %I:%M:%S"
        }
    },
}

mylogger = logging
mylogger.config.dictConfig(LOGGING_CONFIG)

