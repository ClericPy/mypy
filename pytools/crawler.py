
import inspect
import os
import sqlite3
import time
from platform import platform
from threading import Timer

from py_snippets.saver import Saver
from torequests import Async

from . import rules
from .sync_db import sync


# 文章：article（list）；问答：issue（list）；课程：course（list）；资讯：news（list）；更新时间：time（timestamp）。


def ttime(rawtime=None, tzone=8 * 3600):
    try:
        rawtime = time.time() if rawtime is None else rawtime
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(str(rawtime)[:10]) + time.timezone + tzone))
    except:
        return 'error'


def logit(string):
    log_string = '%s --- %s\n\r' % (string, ttime())
    print(log_string)
    with open('./pytools/python_articles/static/errors.txt', 'a', encoding='utf-8') as f:
        f.write(log_string)


def crawl():
    # 获取所有 spider_ 开头的函数
    # 异步采集，存入列表
    # 输出指定格式， title 要去掉首尾空格和网站名称
    '''
  普通文章结构：
  [{'title':'','cover':'','description':'', 'toptime':int,
  'urls':{'source_name':'url'},'time':''},'_id':cleantitle,
   'level':int, 'datetime':ttime,   ,
]
    '''
    # logit('%s\n%s:%s 开始抓取' % ('='*50, platform(), os.getpid()))
    result = rules.get_all()
    # funcs = (Async(i[1])() for i in inspect.getmembers(rules) if i[0].startswith('spider_'))
    # results = [i.x for i in funcs]  # [[dict1,dict2],]
    # results = [i for i in results if i]
    # result = sum(results, [])
    return result


def local_storage():
    # 得到爬虫数据
    # 从数据库把数据取出，合并列表，遇到同一个title的，合并来源网址
    # 重新按时间排序
    # 清理掉超过 maxnum 的部分
    maxnum = 1000000
    toupdate_list = []
    crawl_articles = rules.get_all()
    # print('All crawl missions finished...')
    DB = Saver('./pytools/static/database.db')
    old_articles = DB['article']
    old_articles_dict = {i['_id']: i for i in old_articles}
    old_articles_urls = set()
    for i in old_articles:
        old_articles_urls = old_articles_urls | set(i['urls'].values())
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
            toupdate_list.append(old_articles_dict[i['_id']])
            # old_articles_dict[i['_id']]['like'] = old_articles_dict[i['_id']]['like'] | i['like']
            old_articles_dict[i['_id']]['level'] = max(
                old_articles_dict[i['_id']]['level'], i['level'])
    pre_articles = [old_articles_dict[i] for i in old_articles_dict]
    logit('总计 %s 篇文章，采集到 %s 条数据；新收入 %s 条数据 %s\n%s' % (len(pre_articles), len(
        crawl_articles), len(new_articles), [i['title'] for i in new_articles][:10], '=' * 50))
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
    for i in sync('./pytools/static/database.db',update_list=toupdate_list):
        # 暂时没时间搞, 先全量匹配一次吧...
        print(i)
    conn = sqlite3.connect('./pytools/static/database.db')
    conn.execute("VACUUM")
    conn.execute("VACUUM")
    conn.execute("VACUUM")
    conn.close()
    print('已清理VACUUM...')


def crawler_worker():
    # 先存储，再清理
    # 10 mins timeout & kill myself
    # Timer(10*60, os.kill, (os.getpid(), 9)).start()
    local_storage()
    # logit('数据已存储')
    # os.kill(os.getpid(), 9)


if __name__ == '__main__':
    crawler_worker()
