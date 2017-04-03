from . import python_articles
from sqlitedict import SqliteDict
import flask
import time
import datetime
import re
import psutil
# from fuzzywuzzy.fuzz import ratio
import os

# DB = SqliteDict('./pytools/static/database.db')
# @python_articles.route('/')
# def root():
#     return render_template('index.html')


def ttime(rawtime=None, tzone=8 * 3600):
    try:
        rawtime = time.time() if rawtime is None else rawtime
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(str(rawtime)[:10]) + time.timezone + tzone))
    except:
        return 'error'


def timeago(tt, scope=1):
    tt = int(tt)
    times = []
    if tt == 0:
        return '0 秒'
    for i in zip((31536000, 2592000, 86400, 3600, 60, 1), ('年', '月', '天', '小时', '分钟', '秒')):
        new = tt // i[0]
        if new:
            times.append('%s %s' % (new, i[1]))
        tt = tt - new * i[0]
    return ' '.join(times[:scope])


def check_query(a, b):
    if re.search('\s+', b):
        for i in re.split('\s+', b):
            if str(i).lower() not in str(a).lower():
                return False
        return True
    if not b:
        return True
    if str(b).lower() in str(a).lower():
        return True
    return False


@python_articles.route('/s')
@python_articles.route('/status')
def status():
    try:
        clean = flask.request.args.get('clean', '')
        if clean:
            with open('./pytools/python_articles/static/errors.txt', 'w', encoding='utf-8') as f:
                f.write('')
                return 'Cleaned...'
        server_status = '<h2>当前服务器负载：CPU：{}% ， Memory： {}% ， DB: {} KB </h2>'.format(round(sum(psutil.cpu_times_percent(
        )[:2]), 1), psutil.virtual_memory().percent, os.path.getsize('./pytools/static/database.db') // 1024)
        with open('./pytools/python_articles/static/errors.txt', 'r', encoding='utf-8') as f:
            logs = f.readlines()
            return '<h2><a href="/python_articles/status?clean=1">Clean</a><br />%s</h2>%s' % (server_status, '<br>'.join(logs))
    except Exception as e:
        print(e)
        return e


@python_articles.route('/json')
def json_api():
    try:
        timestamp = flask.request.args.get('timestamp')
        with SqliteDict('./pytools/static/database.db') as DB:
            articles = DB['article']
            total = len(articles)
            if timestamp:
                result = [doc for doc in articles if doc['time']>int(timestamp)]
                return flask.jsonify(result=result, num=total)
            else:
                result = articles[:100]
                return flask.jsonify(result=result, num=total)

    except:
        return '[{}]'


@python_articles.route('/preview/<title>')
def preview(title):
    with SqliteDict('./pytools/static/database.db', autocommit=True) as DB:
        articles = DB['article']
        for i in articles:
            if i['title'] == title:
                return i.get('preview', '该文章未支持预览')

        return '未找到'


@python_articles.route('/settings')
@python_articles.route('/')
def getargv():
    try:
        each_page = 10 if 'Mobile' in flask.request.headers.get(
            'User-Agent', '') else 50
        return flask.render_template('set_argv.html', each_page=each_page)
    except Exception as e:
        print(e)
        return flask.abort(500)


@python_articles.route('/api')
def api():
    try:
        args = flask.request.args
        iscover, autopage, each_page, page, level = (
            args.get(i) or '1' for i in 'iscover autopage each_page page level'.split())
        page = int(page)
        level = int(level)
        each_page = int(args.get('each_page', 0))
        query = args.get('query', '')
        if not each_page:
            each_page = 10 if 'Mobile' in flask.request.headers.get(
                'User-Agent', '') else 50
        with SqliteDict('./pytools/static/database.db', autocommit=True) as DB:
            items = DB['article']
            time1 = time.time()
            items = [{'timeago': timeago(time1 - i['time']), 'title': i['title'][:100], '_id':i.get('_id'), 'article-type': 'normal' if time1 - i['time'] > i['toptime'] else 'top', 'description':('<div class="description" align="left">%s</div>' % i['description']).replace('<p></p>', ''), 'time':i['time'], 'url1':list(i['urls'].values())[0], 'urls':' / '.join(['<a %s target="_blank" href="%s">%s</a>' % ('article-type="hot"' if len(i['urls']) > 1 else '', i['urls'][xx], xx) for xx in i[
                'urls']]), 'cover':('<img src="%s">' % i['cover']).replace('<img src="">', '') if iscover != '0' else '', 'publishedtime':ttime(i['time']), 'levelstar':'<span style="%s">%s</span>' % ('color:#404d5b;' if i.get('level', 1) > 3 else '', '★' * i.get('level', 1))} for i in items if i.get('level', 1) >= level and (check_query(''.join([i.get('title', ''), i.get('description', ''), ''.join(i.get('urls', {}).keys())]), query))][(page - 1) * each_page:page * each_page]
            div_items = '\n'.join(
                ['<div class="py-article" id="{_id}" article-type="{article-type}"><a class="py-head" href="{url1}" target="_blank">{cover}<h3 class="title">{title}</h3></a>{description}<p class="source-url">{urls}</p><div style="width:100%;text-align: right;"><span class="publishedtime" title="{publishedtime}" time="{time}">{timeago}前&emsp;{levelstar}&emsp;</span></div></div>'.format(**item) for item in items])

            return div_items
            # urls = ['<a href="%s"><h1>%s</h1></a>'%(i.name,i.name) for i in funcs]
            # return '<br />'.join(urls)
    except Exception as e:
        print(e)
        return flask.abort(500)


@python_articles.route('/index')
def showall():
    try:
        args = flask.request.args
        if '' in list(args.values()):
            newurl = '%s?%s' % (flask.request.base_url, '&'.join(
                '='.join(i) for i in args.items() if i[1] != ''))
            return flask.redirect(newurl)
        iscover, autopage, each_page, page, level = (
            args.get(i) or '1' for i in 'iscover autopage each_page page level'.split())
        weekly = args.get('weekly')
        page = int(page)
        level = int(level)
        each_page = int(args.get('each_page', 0))
        query = args.get('query', '')
        if not each_page:
            each_page = 10 if 'Mobile' in flask.request.headers.get(
                'User-Agent', '') else 50
        if weekly:
            each_page = 99999
            level = 1
            page = 1

        with SqliteDict('./pytools/static/database.db', autocommit=True) as DB:
            if 'article' not in DB:
                return '没有文章'
            lastCrawl = DB['spider_time']
            items = DB['article']
            if weekly:
                items = [i for i in items if list(map(str, datetime.datetime.fromtimestamp(
                    i['time']).isocalendar()[:2])) == weekly.split('-')]
            new_items = [i for i in items if time.time() -
                         i.get('time', 0) < 30 * 60]
            lastUpdate = max((i.get('time', 0) for i in items))
            time1 = time.time()
            items = [{'timeago': timeago(time1 - i['time']), 'title': i['title'][:100], '_id':i.get('_id'), 'article-type': 'normal' if time1 - i['time'] > i['toptime'] else 'top', 'description':('<div class="description" align="left">%s</div>' % i['description']).replace('<p></p>', ''), 'time':i['time'], 'url1':list(i['urls'].values())[0], 'urls':' / '.join(['<a %s target="_blank" href="%s">%s</a>' % ('article-type="hot"' if len(i['urls']) > 1 else '', i['urls'][xx], xx) for xx in i[
                'urls']]), 'cover':('<img src="%s">' % i['cover']).replace('<img src="">', '') if iscover != '0' else '', 'publishedtime':ttime(i['time']), 'levelstar':'<span style="%s">%s</span>' % ('color:#404d5b;' if i.get('level', 1) > 3 else '', '★' * i.get('level', 1))} for i in items if i.get('level', 1) >= level and (check_query(''.join([i.get('title', ''), i.get('description', ''), ''.join(i.get('urls', {}).keys())]), query))][(page - 1) * each_page:page * each_page]
            div_items = '\n'.join(
                ['<div class="py-article" id="{_id}" article-type="{article-type}"><a class="py-head" href="{url1}" target="_blank">{cover}<h3 class="title">{title}</h3></a>{description}<p class="source-url">{urls}</p><div style="width:100%;text-align: right;"><span class="publishedtime" title="{publishedtime}" time="{time}">{publishedtime}&emsp;{levelstar}&emsp;</span></div></div>'.format(**item) for item in items])
            hidden_query = flask.request.args.copy()
            if 'query' in hidden_query:
                del hidden_query['query']
            hidden_query = ''.join(['<input name="%s" value="%s" style="display:none;" type="text">' % (
                i, hidden_query[i]) for i in hidden_query])
            next1 = flask.request.args.copy()
            next1['page'] = str(int(next1.get('page') or 1) + 1)
            nextpage = '%s?%s' % (
                flask.request.base_url, '&'.join('='.join(i) for i in next1.items()))
            last1 = flask.request.args.copy()
            last1['page'] = str(int(last1.get('page') or 1) - 1)
            lastpage = '%s?%s' % (
                flask.request.base_url, '&'.join('='.join(i) for i in last1.items()))
            pages = '<a target="_self" href="%s">上一页</a> / <a target="_self" href="%s">下一页</a>' % (
                lastpage, nextpage)
            total1 = len(DB['article']) - len(new_items)
            meta_info = '<span style="font-size:0.7em;"> ( lastCrawl：<span title="%s">%s前</span> ; lastUpdate：<span title="%s">%s前</span> ; totalCount：<span>%s</span> )</span>' % (
                ttime(lastCrawl), timeago(time1 - lastCrawl), ttime(lastUpdate), timeago(time1 - lastUpdate), total1)
            return flask.render_template('index.html', firstpage=div_items, pagenum=page, hidden_query=hidden_query, pages=pages, meta_info=meta_info, totalnum='%s + %s' % (total1, len(new_items)), bodywidth=95 if 'Mobile' in flask.request.headers.get('User-Agent', '') else 75)
    except Exception as e:
        print(e)
        return flask.abort(500)
