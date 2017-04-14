import datetime
import hashlib
import re
import os
import time
import pymongo
import traceback
import sqlite3
from collections import Counter

import requests

from py_snippets.saver import Saver


def md5(x): return hashlib.md5(str(x).encode('utf-8')).hexdigest()[8:-8]


mongodb_uri = os.environ.get('MONGODB_URI_LD')


def ttime(rawtime=None, tzone=8 * 3600):
    try:
        rawtime = time.time() if rawtime is None else rawtime
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(str(rawtime)[:10]) + time.timezone + tzone))
    except:
        return 'error'


def time2week(time1):
    pass


def update_online_docs():
    try:
        with pymongo.MongoClient(mongodb_uri) as client:
            collection = client.heroku_ggpxscwz.article
            mongo_docs = list(collection.find())
            update_list = [
                i for i in mongo_docs if '稀土掘金' in list(i['urls'].keys())]
            print(len(update_list))
            for x, item in enumerate(update_list, 1):
                item['cover'] = ''
                collection.update_one({'_id': item['_id']}, {
                    '$set': item}, upsert=True)

                print(x, '/', len(update_list), item['title'])
    except:
        traceback.print_exc()
    input('over...')


def db_init_tool():
    db = Saver('database.db', 'sqlitedict')
    init_state = {
        'spider_time': 0, 'updatetime': '2017-04-05 02:31:30',
        'spider_status': 'free', 'time': 0,
        'article': [
            {'_id': '提高你的python解释yield和generators生成器', 'cover': '',
             'description': '2017-04-11', 'level': 3, 'time': 1491927304,
             'title': '服务器正在初始化, 请稍候', 'toptime': 0, 'urls':
             {'Github': 'https://github.com/ClericPy'}}
        ]}
    db.update(init_state)

    conn = sqlite3.connect('database.db')
    conn.execute("VACUUM")
    conn.execute("VACUUM")
    conn.execute("VACUUM")
    conn.close()


# update_online_docs()
db_init_tool()
