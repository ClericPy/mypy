import datetime
import os
import re
import sys
import time
import traceback
from collections import Counter
from py_snippets.retry import retry
import requests

from sqlitedict import SqliteDict


def ttime(rawtime=None, tzone=8 * 3600):
    try:
        rawtime = time.time() if rawtime is None else rawtime
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(str(rawtime)[:10]) + time.timezone + tzone))
    except:
        return 'error'


def time2week(time1):
    pass

@retry(5,1,1)
def sync_docs():
    with SqliteDict('database.db', autocommit=True) as DB:
        ss = DB['article']
        print(len(ss), 'local datas')
        r = requests.get(
            'https://github.com/ClericPy/mypy/blob/master/pytools/static/database.db')
        # print(r.text)
        # sys.exit()
        last_doc_time = int(time.mktime(time.strptime(re.findall(
            'datetime="(.*?)"', r.text)[0], '%Y-%m-%dT%H:%M:%SZ')) + 8 * 3600)
        print(last_doc_time)

        r = requests.get(
            'https://pyld.herokuapp.com/python_articles/json?timestamp=%s' % (last_doc_time))
        items = r.json()['result']
        print(len(items), 'gotcha docs...')
        items = [i for i in items if i not in ss]
        print(len(items), 'new docs...')
        if not items:
            return
        # ======================================================
        crawl_articles = items
        maxnum = 1000000
        old_articles = DB.get('article', [])
        old_articles_dict = {i['_id'].lower(): i for i in old_articles}
        old_articles_urls = set()
        for i in old_articles:
            old_articles_urls = old_articles_urls | set(i['urls'].values())
        # old_articles_keys = set(old_articles_dict.keys())
        # crawl_articles1 = {i for i in crawl_articles if not i.keys() & old_articles_keys}
        new_articles = []
        for i in crawl_articles:
            if set(i['urls'].values()) & old_articles_urls:
                continue
            if i['_id'] not in old_articles_dict.keys():
                new_articles.append(i)
                # old_articles_keys = old_articles_keys | {i['_id']}
                old_articles_dict[i['_id']] = i
            else:
                old_articles_dict[i['_id']]['urls'].update(i['urls'])
                # old_articles_dict[i['_id']]['like'] = old_articles_dict[i['_id']]['like'] | i['like']
                old_articles_dict[i['_id']]['level'] = max(
                    old_articles_dict[i['_id']]['level'], i['level'])
        pre_articles = [old_articles_dict[i] for i in old_articles_dict]
        print('总计 %s 篇文章，采集到 %s 条数据；新收入 %s 条数据 %s\n%s' % (len(pre_articles), len(
            crawl_articles), len(new_articles), '...', '=' * 50))
        sorted_articles = sorted(
            pre_articles, key=lambda x: (x['time'], x['level'], x['_id']), reverse=True)
        # 置顶文章放到前面，过期置顶不用管，等它自己排序被排出500外。
        tops = []
        meta_data = sorted_articles[:]
        time1 = time.time()
        normal_articles_not_clean = (
            x if time1 - x['time'] > x['toptime'] else tops.append(meta_data[i]) for i, x in enumerate(sorted_articles))
        normal_articles = [i for i in normal_articles_not_clean if i]
        DB['article'] = (tops + normal_articles)[:maxnum]
        DB['time'] = time.time()
        DB['updatetime'] = ttime()
try:
    sync_docs()
except:
    traceback.print_exc()
    input('Waiting for enter.')

os.system('pause')
