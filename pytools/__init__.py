
import os
import random
import time
from threading import Timer

import flask
import psutil
import requests

from .crawler import crawler_worker
from .python_articles import python_articles
from .sync_db import sync
from py_snippets.saver import Saver


def ttime(rawtime=None, tzone=8 * 3600):
    try:
        rawtime = time.time() if rawtime is None else rawtime
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(str(rawtime)[:10]) + time.timezone + tzone))
    except:
        return 'error'


with open('pytools/python_articles/static/errors.txt', 'w', encoding='utf-8') as f:
    f.write('')


def logit(string):
    log_string = '%s --- %s\n\r' % (string, ttime())
    print(log_string)
    with open('./pytools/python_articles/static/errors.txt', 'a', encoding='utf-8') as f:
        f.write(log_string)

app = flask.Flask(__name__)

DB = Saver('./pytools/static/database.db', mode='sqlitedict')
DB['spider_status'] = 'free'
DB['spider_time'] = 0
not_sync_yet = 1
# os.environ['downloaddb'] = 'aa'

funcs = [python_articles, ]

for bp in funcs:
    app.register_blueprint(bp)


def randomtime():
    # 就是简单生成个时间让多进程的任务错开避免死锁，也避免爬虫频率太准确
    return random.randint(0, 5) + random.random()


@app.route('/ddb', methods=['post', 'get'])
def downdb():
    return flask.send_file('./static/database.db',
                           as_attachment=True,
                           attachment_filename='database.db')
    # if flask.request.method == 'GET':
    # return '''<form action="/database.db" method="post">口令：<input
    # type="text" name="pw" />
    # <input type = "submit" value = "提交" / > < /form >'''
    # if flask.request.method == 'POST':
    #     if flask.request.form.get('pw','') == os.environ.get('downloaddb',''):
    #         return app.send_static_file('database.db')
    #     else:
    #         return 'invalid password'


@app.route('/server_status')
def server_status():
    try:
        cpu1 = sum(psutil.cpu_times_percent()[:2])
        mem1 = round(psutil.virtual_memory().percent, 1)
        db_size = round(
            os.path.getsize('pytools/static/database.db') / (1024 * 1024), 3)
        ss = '<h1>CPU: {} % <br>内存: {} %<br> DB_size: {} MB</h1>'.format(
            cpu1, mem1, db_size)
        print(ss)
        return ss
    except Exception as e:
        print(e)


@app.route('/')
def showall():
    try:
        return flask.redirect('/python_articles/index')
        # ss = DB['article']
        # return flask.jsonify({'data': ss, 'time': [DB['updatetime'], DB['time']]})
        # urls = ['<a href="%s"><h1>%s</h1></a>'%(i.name,i.name) for i in funcs]
        # return '<br />'.join(urls)
    except Exception as e:
        return str(e)


# @app.route('/database.db')
# def root():
#     return app.send_static_file('database.db')

def time_machine():
    # print('启动爬虫： %s' % os.getpid())
    # 每隔 5 分钟检测一次，如果爬虫worker空闲，且上次完成时间已经过去30分钟，则执行爬虫子进程。
    global not_sync_yet
    if not_sync_yet:  # :
        for i in sync('./pytools/static/database.db', os.environ.get('DOWNLOAD_FROM_MONGODB')):
            logit(i)
        not_sync_yet = 0
    while 1:
        try:
                # DB['spider_status'] = 'free'
                # DB['spider_time'] = 0
            spider_status = DB['spider_status']
            spider_time = DB['spider_time']
            spider_time_passed = time.time() - spider_time
            if spider_status != 'free':
                print('PID %s : 发现爬虫进程 %s 正在运行，pass...' %
                      (os.getpid(), spider_status))
                break
            if spider_time_passed < 30 * 60:
                tt = spider_time_passed
                htime = '%s 小时' % (tt // 3600) if tt // 3600 > 0 else ''
                mtime = '%s 分钟' % (
                    (tt % 3600) // 60) if (tt % 3600) // 60 > 0 else ''
                stime = '%s 秒' % (int((tt % 3600) % 60))
                print('PID %s : 上次抓取发生在 %s %s %s 之前(%s)，最小抓取间隔为 30 min，所以跳过本次循环。' %
                      (os.getpid(), htime, mtime, stime, ttime(spider_time)))
                break
            if spider_status == 'free' and spider_time_passed >= 30 * 60:
                # 阻塞其他进程发起爬虫命令，完成后修改爬虫
                DB['spider_status'] = str(os.getpid())
                print('PID %s :  开始采集数据。' % (os.getpid()))
                crawler_worker()
                DB['spider_time'] = time.time()
                DB['spider_status'] = 'free'
                print('PID %s : 采集结束。%s' % (os.getpid(), ttime()))
                print('当前服务器负载：CPU：{}% ， Memory： {}%'.format(
                    round(sum(psutil.cpu_times_percent()[:2]), 1), psutil.virtual_memory().percent))

                break

            break
        except Exception as e:
            print('5分钟后 %s 出错重试 : %s' % (os.getpid(), e))
            DB['spider_time'] = time.time()
            DB['spider_status'] = 'free'
            time.sleep(randomtime() + 300)
            continue
    Timer(10 * 60 + randomtime(), time_machine).start()


print('Open spider. pid: %s' % os.getpid())
Timer(randomtime(), time_machine).start()
