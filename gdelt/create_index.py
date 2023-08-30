import requests
import os, sys

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from requests.auth import HTTPBasicAuth
import json
from ci.logger import logger

ES_HOST = os.environ.get("ES_HOST")
ES_USER = os.environ.get("ES_USER")
ES_PASSWORD = os.environ.get("ES_PASSWORD")
ES_GDELT_INDEX = os.environ.get("ES_EVENTS_INDEX")
ES_GKG_INDEX = os.environ.get("ES_GKG_INDEX")
ES_MENTIONS_INDEX = os.environ.get("ES_MENTIONS_INDEX")
INDEX = ES_GKG_INDEX
URL = ES_HOST


def create_indice(delete=None):

    headers = {
        "Content-Type": "application/json"
    }

    
    
    # URL += "/_template"
    logger.debug(URL)
    PATH = abspath(join(dirname(__file__), '.'))
    template = open(f"{PATH}/elasticsearch/gkg-template.json").read()
    template = json.loads(template)

    template_name = template['template']
    template.pop('template')

    res = requests.put(URL + f"_template/{template_name}", json=template, auth=HTTPBasicAuth(ES_USER, ES_PASSWORD), headers=headers)

    logger.debug(res.content)


if __name__ == "__main__":
    logger.debug(__file__)    
    create_indice(INDEX)