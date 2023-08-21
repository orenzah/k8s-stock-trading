import os
import zipfile
import requests
import sys
import datetime

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))


import json
from ci.logger import logger

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_PATH = os.path.join(BASE_PATH, "")
ZIP_EXTRACT_PATH = os.path.join(BASE_PATH, "data", "realtime")



def download_file(url):
    logger.debug( f'downloading: {url}')
    """

    :param url:
    :return:
    """    
    local_filename = url.split('/')[-1]
    local_filename = os.path.join(DOWNLOAD_PATH, local_filename)
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    if not r.ok:
        logger.debug( "request returned with code {}".format(r.status_code))
        return None
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def unzip(path):
    logger.debug(f'unzipping: {path}')
    zip_ref = zipfile.ZipFile(path, 'r')
    zip_ref.extractall(ZIP_EXTRACT_PATH)
    zip_ref.close()


def get(_from_date=None):
    """

    :param _from_date:
    :return:
    """

    feeds = [
        "http://data.gdeltproject.org/gdeltv2/lastupdate.txt",
        "http://data.gdeltproject.org/gdeltv2/lastupdate-translation.txt"
    ]

    for feed in feeds:
        if not _from_date:
            res = requests.get(feed)
            logger.debug( res.encoding)
            
            res.content
            url = None
            gkg_url = None
            mentions_url = None
            content = bytes(res.content).decode("utf-8")
            logger.debug( content)
        
            for line in content.split("\n"):                
                if not line:
                    continue

                if line.count(".export.CSV.zip") > 0:
                    url = line.split(" ")[2]
                if line.count(".gkg.csv.zip") > 0:
                    gkg_url = line.split(" ")[2]
                if line.count(".mentions.CSV.zip") > 0:
                    mentions_url = line.split(" ")[2]


            if not url or not gkg_url:
                return
        else:
            if feed.count("translation") > 0:
                _from_date += ".translation"

            url = f"http://data.gdeltproject.org/gdeltv2/{_from_date}.export.CSV.zip"
            mentions_url = f"http://data.gdeltproject.org/gdeltv2/{_from_date}.mentions.CSV.zip"
            gkg_url = f"http://data.gdeltproject.org/gdeltv2/{_from_date}.gkg.csv.zip"

            logger.debug( url)
            logger.debug( gkg_url)
            logger.debug( mentions_url)


        filename = download_file(url)        
        filename_gkg = download_file(gkg_url)
        filename_mentions = download_file(mentions_url)
        if filename:
            unzip(filename)
            os.remove(filename)

            unzip(filename_gkg)
            os.remove(filename_gkg)

            unzip(filename_mentions)
            os.remove(filename_mentions)


if __name__ == "__main__":
    """
    To download the current 15 mins update use (good for cron jobs):
    python gdelt_realtime_downloader.py
    To download a time range (good when cron jobs or internet connection fails :))
    python gdelt_realtime_downloader.py 2017-07-12T10:00 2017-07-12T11:00
    """
    if len(sys.argv) > 1:
        _from_date = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%dT%H:%M")
        _to_date = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M")
        if _from_date > _to_date:
            raise Exception("{0} must be after {1}".format(_from_date, _to_date))

        while _from_date <= _to_date:
            get(_from_date.strftime("%Y%m%d%H%M%S"))
            _from_date = _from_date + datetime.timedelta(minutes=15)
    else:
        get()