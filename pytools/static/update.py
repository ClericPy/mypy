import datetime
import hashlib
import re
import time
import sqlite3
from collections import Counter

import requests

from sqlitedict import SqliteDict

md5 = lambda x: hashlib.md5(str(x).encode('utf-8')).hexdigest()[8:-8]


def ttime(rawtime=None, tzone=8 * 3600):
    try:
        rawtime = time.time() if rawtime is None else rawtime
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(str(rawtime)[:10]) + time.timezone + tzone))
    except:
        return 'error'


def time2week(time1):
    pass


def update_docs():
    with pymongo.MongoClient(mongodb_uri) as client:
        collection = client.heroku_ggpxscwz.article
        update_list = []


update_docs()
