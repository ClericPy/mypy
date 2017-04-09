import datetime
import hashlib
import re
import os
import time
import pymongo
from collections import Counter

import requests

from sqlitedict import SqliteDict

md5 = lambda x: hashlib.md5(str(x).encode('utf-8')).hexdigest()[8:-8]
mongodb_uri = os.environ.get('MONGODB_URI_LD')

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
        mongo_docs = list(collection.find())
        update_list = [
            i for i in mongo_docs if '知乎专栏-' in list(i['urls'].keys())[0]]
        print(len(update_list))
        for x,item in enumerate(update_list,1):
            item['cover'] = ''
            collection.update_one({'_id': item['_id']}, {
                                              '$set': item}, upsert=True)

            print(x,'/',len(update_list),item['title'])
                                        
update_docs()
