import datetime
import hashlib
import re
import time
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
    with SqliteDict('database.db', autocommit=True) as DB:
        ss = DB['article']
        # print(len(ss),len(set([i['title'] for i in ss])))
        print(ss[0])
        # input()
        # for i in ss:
        #     i['_id'] = i.pop('id')
        #     i['md5'] = md5(i['_id'])
        #     i['datetime'] = ttime(i['time'])
        # # print(max([i['time'] for i in ss]))
        # DB['article'] = ss
        print('done')


update_docs()
