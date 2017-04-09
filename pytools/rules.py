#!python3
import datetime
import hashlib
import json
import random
import re
import time
from html import unescape
from urllib.parse import quote, unquote

from jsonpath_rw_ext import parse
from lxml.html import fromstring, tostring
from torequests import Async, threads, tPool


def md5(x):
    return hashlib.md5(str(x).encode('utf-8')).hexdigest()[8:-8]


class Null(object):

    def __init__(self, *args, **kwargs):
        return

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, mname):
        return self

    def __setattr__(self, name, value):
        return self

    def __getitem__(self, key):
        return self

    def __delattr__(self, name):
        return self

    def __repr__(self):
        return ""

    def __str__(self):
        return ""

    def __bool__(self):
        return False


def get_true(sth):
    return sth or ''

null = Null()
trequests = tPool(50)
thisday = datetime.datetime.today()
# time1 = int(time.time())

http_local_proxy = list(
    {"101.226.249.237:80", "122.147.24.103:8080", "81.82.240.15:8080", "194.102.229.246:80"})
headers = {'User-Agent':
           'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0', 'Connection': 'close'}
# proxies = {'http':None,'https':None}


default_args = dict(headers=headers, timeout=20)


def jp(raw_json, jsonpath):
    jsonpath = parse(jsonpath)
    return [i.value for i in jsonpath.find(raw_json)]


def logit(string):
    log_string = '%s --- %s\n\r' % (string, ttime())
    print(log_string)
    with open('./pytools/python_articles/static/errors.txt', 'a', encoding='utf-8') as f:
        f.write(log_string)


def getlist1(list1):
    if type(list1) != list:
        return list1
    return list1[0] if list1 else ''


def ttime(rawtime=None, tzone=8 * 3600):
    try:
        rawtime = time.time() if rawtime is None else rawtime
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(str(rawtime)[:10]) + time.timezone + tzone))
    except:
        return 'error'


def schema_check(docs):
    assert type(docs) is list, 'It\'s not list'
    assert len(docs) > 0, 'empty list'
    for doc in docs:
        assert list(doc['urls'].values())[0].startswith(
            'http') is True, '%s url not startswith http' % doc
        assert type(doc.get('title')) is str, '%s title is not string' % doc
        assert doc['cover'].startswith(
            ('http', 'static/pics/')) is True or doc['cover'] == '', '%s bad cover' % doc
    return 'ok'


def cleanid(title):
    new_id = re.sub('_|0x|\W+|^Show HN:\s*', '', str(title))
    # 在python3里，\W也包括了中文标点，就是这么强,\w却包括了中文，就这么爽
    # new_id = re.sub('\s+|[，。！@￥%…&（）【】｛｝：；“”‘’《》？、·\-_]+|0x|\W+', '',
    # str(title))
    return new_id.lower()
    # print(cleanid(' 中文\t，。！@#￥%…&（）【】｛｝：[]\\；“”‘’《》？、·!@#$*-_=+,./?~'))
# result = [{'title': title, '_id': cleanid(title), 'level': level,
# 'cover': cover, 'description': description, 'toptime': 0, 'urls':
# {source_name: url}, 'time': time1}]


def common_zhihu_zhuanlan(url, source_name):
    source_name = '知乎专栏-%s' % source_name
    time1 = int(time.time())
    level = 3
    if not url.startswith('http'):
        url = 'https://zhuanlan.zhihu.com/api/columns/%s/posts?limit=20' % url
    r = trequests.get(url, retry=1, **default_args)
    items = r.json()
    if not items:
        logit('%s 解析失败.' % source_name)
        return
    titles = [unescape(i.get('title', '').strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = ['https://zhuanlan.zhihu.com%s' % i.get('url', '') for i in items]
    descriptions = [re.sub('<[\s\S]*?>','',unescape(i.get('content') or ''))[:30] for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_bole_article(proxy=None):
    source_name = '伯乐文章'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://python.jobbole.com/all-posts/', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath(
        '//div[@id="archive"]/div[@class="post floated-thumb"]')
    titles = [unescape(getlist1(i.xpath(
        './div[@class="post-meta"]/p/a[@class="archive-title"]/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    # covers = [getlist1(i.xpath('./div[@class="post-thumb"]//img/@src')) for
    # i in items]
    covers = [''] * len(titles)
    descriptions1 = [unescape(getlist1(i.xpath(
        './div[@class="post-meta"]/span[@class="excerpt"]/p/text()'))[:50]) for i in items]
    urls = [getlist1(i.xpath('./div[@class="post-thumb"]/a/@href'))
            for i in items]
    times = [getlist1(
        i.xpath('./div[@class="post-meta"]/p[1]')).text_content() for i in items]
    times = [getlist1(re.findall('20\d\d/\d\d/\d\d', i)) for i in times]
    descriptions = ['...'.join(i) for i in zip(descriptions1, times)]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_python_weekly(proxy=None):
    # 置顶24小时
    source_name = 'Python Weekly'
    time1 = int(time.time())
    level = 4
    r = trequests.get(
        'http://us2.campaign-archive1.com/home/?u=e2e180baf855ac797ef407fc7&id=9e26887fc5', proxies=proxy, **default_args)
    scode = r.text
    item = getlist1(re.findall('<li class="campaign">(.*?)</li>', scode))
    title = getlist1(re.findall('title="(.*?)"', item)).strip()
    title = unescape(title)
    thetime = getlist1(re.findall('(\d\d/\d\d/\d\d\d\d) - ', item)).strip()
    cover = 'static/pics/python_weekly.png'
    url = getlist1(re.findall('href="(.*?)"', item))
    description = 'Welcome to Python Weekly. We have a packed issue this week. Enjoy it! [%s]<br /><a href="http://us2.campaign-archive1.com/home/?u=e2e180baf855ac797ef407fc7&id=9e26887fc5">Other Issues</a> | <a href="http://us2.campaign-archive2.com/home/?u=e2e180baf855ac797ef407fc7&id=9e26887fc5">Backup URL</a>' % thetime
    result = [{'title': title, '_id': cleanid(title), 'level': level, 'cover': cover, 'description': description, 'toptime': 24 * 3600, 'urls': {
        source_name: url}, 'time': time1}]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_pycoders_weekly(proxy=None):
    # 置顶24小时
    source_name = 'Pycoders Weekly'
    time1 = int(time.time())
    level = 4
    sourceurl = 'http://us4.campaign-archive1.com/home/?u=9735795484d2e4c204da82a29&id=64134e0a27'
    r = trequests.get(
        sourceurl, proxies=proxy, **default_args)
    scode = r.text
    css = fromstring(scode).cssselect('#archive-list li a') or null

    title = unescape(css[0].text or '')
    cover = 'static/pics/pycoders.png'
    url = unquote(css[0].get('href', '') or '')
    description = 'Pycoders Weekly dose of all things Python. <a target="_blank" href="%s">Past Issues</a>' % sourceurl
    result = [{'title': title, '_id': cleanid(title), 'level': level, 'cover': cover, 'description': description, 'toptime': 24 * 3600, 'urls': {
        source_name: url}, 'time': time1}]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_importpython(proxy=None):
    # 置顶24小时
    source_name = 'Import Python'
    time1 = int(time.time())
    level = 4
    r = trequests.get(
        'http://importpython.com/newsletter/archive/', proxies=proxy, **default_args)
    scode = r.text
    items = fromstring(
        r.content.decode('utf-8')).cssselect('.container> .row .thumbnail')[:10]
    titles = [
        unescape((i.cssselect('h4') or null)[0].text or '').strip() for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = ['http://importpython.com' +
            ((i.cssselect('.caption>a') or null)[0].get('href') or '') for i in items]
    descriptions = [unescape(
        (i.cssselect('div>div:nth-child(2) ') or null)[0].text or '').strip() for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_pythondaily(proxy=None):
    # 置顶24小时
    source_name = '好东西传送门-Python日报'
    time1 = int(time.time())
    level = 4
    times = [ttime(time.time() + 24 * 3600 * n) for n in range(-1, 2)]
    rawurl = ['http://forum.ai100.com.cn/blog/thread/py-%s/' %
              i.split(' ')[0] for i in times]
    rs = [
        [url1, trequests.get(url1, proxies=proxy, **default_args)] for url1 in rawurl]
    scodes = [[r[0], r[1].x.content.decode('utf-8')] for r in rs if r[1].x]
    if not scodes:
        result = []
        print('%s finished: %s gotten.' % (source_name, len(result)))
        # assert len(result) > 0, '%s 抓取结果为 0。' % source_name
        return result

    items = [i for i in scodes if '未找到页面 | 好东西论坛' not in i[1]]
    result = [{'title': getlist1(re.findall('<meta itemprop="name" content="(.*?)"/>', i[1])), '_id':cleanid(getlist1(re.findall('<meta itemprop="name" content="(.*?)"/>', i[1]))), 'level':level, 'cover':'static/pics/pythondaily.jpg',
               'description':getlist1(re.findall('<div id="headline-wrapper">([\s\S]+?)</div>', i[1])).replace('<a ', '<span ').replace('</a>', '</span>'), 'toptime':24 * 3600, 'urls':{source_name: i[0]}, 'time':time1} for i in items]
    result = [i for i in result if i.get('title')]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    # assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_weekly_manong(proxy=None):
    # 置顶24小时
    source_name = '码农周刊'
    time1 = int(time.time())
    level = 4
    r = trequests.get(
        'http://weekly.manong.io/issues/', proxies=proxy, **default_args)
    scode = r.text
    # head =
    # tostring(fromstring(preview1).xpath('//head/style')[0]).decode('utf-8')
    item = fromstring(scode).xpath('//div[@class="issue"][1]')[0]
    title = getlist1(item.xpath('./p/text()'))
    title = unescape(title)
    cover = ''
    url = getlist1(item.xpath('./h4/a/@href'))
    description = '码农周刊是一份专为程序员打造的IT技术周刊，精选一周IT技术干货，每周一发送，完全免费。'
    result = [{'title': title, '_id': cleanid(title), 'level': level, 'cover': cover, 'description': description, 'toptime': 24 * 3600, 'urls': {
        source_name: url}, 'time': time1}]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_weekly_pychina(proxy=None):
    # 置顶24小时
    source_name = '蠎周刊'
    time1 = int(time.time())
    level = 4
    r = trequests.get(
        'http://weekly.pychina.org/', proxies=proxy, **default_args)
    scode = r.content.decode('utf-8')
    # head = tostring(fromstring(preview1).xpath('//head/style')[0]).decode('utf-8')
    # 只取前两篇
    items = fromstring(scode).xpath('//article')[:2]
    titles = [unescape(getlist1(item.xpath('./h2/a/text()')))
              for item in items]
    covers = ['static/pics/mangzhoukan.png'] * len(titles)
    urls = [getlist1(item.xpath('./h2/a/@href')) for item in items]
    descriptions = [
        '英文出处: ' + tostring(item.xpath('./div[@class="summary"]/ul[1]/li/a')[0]).decode('utf-8') for item in items]
    # [getlist1(item.xpath('./div[@class="summary"]/ul[1]/li')) for item in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':24 * 3600, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_jb51_python(proxy=None):
    source_name = '脚本之家'
    time1 = int(time.time())
    level = 2
    r = trequests.get(
        'http://www.jb51.net/list/list_97_1.htm', proxies=proxy, **default_args)
    items = fromstring(r.content.decode('gb18030')).xpath(
        '//div[@class="artlist clearfix"]/dl/dt')
    titles = [unescape(getlist1(i.xpath('./a/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [
        'http://www.jb51.net' + getlist1(i.xpath('./a/@href')) for i in items]
    descriptions = [
        unescape(getlist1(i.xpath('./span/text()')).strip()) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def no_spider_csdn_blog_python():
    source_name = 'CSDN博客'
    time1 = int(time.time())
    level = 2
    r = trequests.get(
        'http://blog.csdn.net/tag/details.html?tag=python', proxies=proxy, **default_args)
    # print(r.text)
    items = json.loads(
        getlist1(re.findall('var data = (.*?);', r.text))).get('result')
    if not items:
        logit('%s 解析失败.' % source_name)
        return
    titles = [
        unescape('%s [%s]' % (i.get('title', ''), i.get('created_at', '')[:8])) for i in items]
    if ' []' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [i.get('url', '') for i in items]
    descriptions = [''] * len(titles)
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_geek_python(proxy=None):
    source_name = '极客头条'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://geek.csdn.net/forum/68?t=h', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//dl[@class="geek_list"]/dd')
    titles = [
        unescape(getlist1(i.xpath('.//a[@class="title"]/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [getlist1(i.xpath('.//a[@class="title"]/@href')) for i in items]
    descriptions = [''] * len(titles)
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_xitu_gold(proxy=None):
    source_name = '稀土掘金'
    time1 = int(time.time())
    level = 3
    headers1 = headers.copy()
    headers1.update({"x-avoscloud-request-sign": "dd36c74cb860e12f7e12ac1c9c14917f,2139632477696",
                     "X-avoscloud-Application-Id": "mhke0kuv33myn4t4ghuid4oq2hjj12li374hvcif202y5bm6"})
    r = trequests.get(
        'https://api.leancloud.cn/1.1/classes/Entry?include=user,user.installation&limit=15&order=-createdAt&where={"tags":{"__type":"Pointer","className":"Tag","objectId":"559a7227e4b08a686d25744f"}}', timeout=20, headers=headers1)
    # print(r.text)
    items = r.json().get('results', [])
    if not items:
        logit('%s 解析失败.' % source_name)
        return
    titles = [unescape(i.get('title', '').strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [getlist1(jp(i, '$.screenshot.url')) for i in items]
    urls = [i.get('originalUrl', 'http://gold.xitu.io/#/tag/Python')
            for i in items]
    descriptions = [unescape(i.get('createdAt', '').split('T')[0])
                    for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_planet_python(proxy=None):
    source_name = 'Planet Python'
    time1 = int(time.time())
    level = 3
    r = trequests.get('http://planetpython.org/',
                      proxies=proxy, **default_args)
    items = re.findall(
        '(<h3 class="post">[\s\S]*?</h4>)', r.content.decode('utf-8'))
    titles = [unescape(getlist1(re.findall('<h4><a.*?>(.*?)</a></h4>', i)))
              for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [
        getlist1(re.findall('<h4><a.*?href="(.*?)".*?>.*?</a></h4>', i)) for i in items]
    descriptions = [
        unescape(getlist1(re.findall('<h3 class="post">(.*?)</h3>', i))) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def old_spider_oschina_translate(proxy=None):
    source_name = '开源中国'
    time1 = int(time.time())
    level = 4
    r = trequests.get(
        'http://www.oschina.net/translate/tag/python', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//div[@class="article"]')[:10]
    titles = [
        unescape(getlist1(i.xpath('./dl/dt/a/@title')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [getlist1(i.xpath('./dl/dt/a/@href')) for i in items]
    descriptions = [
        unescape(getlist1(i.xpath('./dl/dd[@class="content"]/text()'))) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':24 * 3600, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_bole_toutiao(proxy=None):
    source_name = '伯乐头条'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://top.jobbole.com/tag/python/?sort=latest', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//li[@class="media"]')
    titles = [
        unescape(getlist1(i.xpath('./div/h3/a/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [getlist1(i.xpath('./div/h3/a/@href')) for i in items]
    descriptions = [''] * len(titles)
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_phpxs_daimapianduan(proxy=None):
    source_name = '代码片段'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://www.phpxs.com/code/python', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//li[@class="archive-simple"]')
    titles = [
        unescape(getlist1(i.xpath('./h2/a/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = ['http://www.phpxs.com%s' %
            getlist1(i.xpath('./h2/a/@href')) for i in items]
    descriptions = [
        unescape(getlist1(i.xpath('./p/span[1]/text()')).strip()) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_jb51_ebook(proxy=None):
    source_name = '脚本之家(eBook)'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://www.jb51.net/books/list476_1.html', proxies=proxy, **default_args)
    items = fromstring(r.content.decode('gb18030')).xpath(
        '//ul[@class="cur-cat-list"]/li')
    # print(r.content.decode('gbk'))
    # return
    titles = [
        unescape(getlist1(i.xpath('.//a[@class="tit"]/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [
        'http://www.jb51.net' + getlist1(i.xpath('.//a[@class="tit"]/@href')) for i in items]
    descriptions = [
        unescape(getlist1(i.xpath('.//dd[@class="desc"]/text()')).strip()) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':3600 * 6, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_python_hackernews(proxy=None):
    source_name = 'Hacker News'
    time1 = int(time.time())
    level = 4
    r = trequests.post('https://uj5wyc0l7x-dsn.algolia.net/1/indexes/Item_production_sort_date/query?X-Algolia-API-Key=8ece23f8eb07cd25d40262a1764599b1&X-Algolia-Application-Id=UJ5WYC0L7X',
                       data='{"params":"query=python&hitsPerPage=20&minWordSizefor1Typo=5&minWordSizefor2Typos=9&advancedSyntax=true&ignorePlurals=false&tagFilters=%5B%22story%22%5D&numericFilters=%5B%22created_at_i%3E1459356642.649%22%5D&page=0&queryType=prefixLast&typoTolerance=false&restrictSearchableAttributes=%5B%5D"}', proxies=proxy, **default_args)
    items = r.json().get('hits', [])
    if not items:
        logit('%s 解析失败.' % source_name)
        return
    titles = [
        unescape(i.get('title', '').strip().replace('Show HN: ', '')) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = [i.get('url', '') or '' for i in items]
    descriptions = ['<a href="https://news.ycombinator.com/item?id=%s">Comments</a>' %
                    i.get('objectID', '') for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_news_codingpy(proxy=None):
    source_name = '编程派'
    time1 = int(time.time())
    level = 4
    r = trequests.get('http://codingpy.com/', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//div[@class="js-infinite-item"]')
    titles = [unescape(getlist1(i.xpath('.//h2/text()')).strip())
              for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['http://codingpy.com%s' %
              getlist1(i.xpath('.//div[@class="image "]/div/@data-bg')).strip() for i in items]
    urls = [getlist1(i.xpath('.//div[@class="header"]/a/@href'))
            for i in items]
    descriptions = [
        unescape(getlist1(i.xpath('.//div[@class="description"]/text()')).strip()) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_segmentfault_article(proxy=None):
    source_name = 'SegmentFault'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'https://segmentfault.com/t/python/blogs', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath(
        '//div[@class="stream-list blog-stream"]/section')
    titles = [unescape(getlist1(i.xpath('.//h2/a/text()')).strip())
              for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(items)
    urls = ['https://segmentfault.com%s' %
            getlist1(i.xpath('.//h2/a/@href')) for i in items]
    descriptions = [unescape(getlist1(i.xpath(
        './/p[@class="excerpt wordbreak hidden-xs"]/text()')).strip()) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_tuicool_article(proxy=None):
    source_name = '推酷'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://www.tuicool.com/topics/11130000?st=1&lang=0', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//div[@class="list_article_item"]')
    titles = [unescape(getlist1(
        i.xpath('.//div[@class="title"]/a/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [getlist1(i.xpath('.//div[@class="article_thumb_image"]/img/@src')).replace(
        'http://static0.tuicool.com/images/abs_img_no_small.jpg', '') for i in items]
    urls = ['http://www.tuicool.com%s' %
            getlist1(i.xpath('.//div[@class="title"]/a/@href')) for i in items]
    descriptions = [
        unescape(re.sub('\s+', ' ', getlist1(i.xpath('.//div[@class="tip"]')).text_content())) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_python_china(proxy=None):
    source_name = 'Python China'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://python-china.org/api/topics/timeline', retry=1, proxies=proxy, **default_args)
    items = r.json().get('data', [])
    if not items:
        logit('%s 解析失败.' % source_name)
        return
    titles = [unescape(i.get('title', '').strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [''] * len(titles)
    urls = ['http://python-china.org/t/%s' %
            i.get('id', '') or '' for i in items]
    descriptions = [''] * len(titles)
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    # assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_doughellmann_article(proxy=None):
    # 置顶3小时
    source_name = 'Doug Hellmann\'s Blog'
    time1 = int(time.time())
    level = 4
    r = trequests.get(
        'https://doughellmann.com/blog/', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//main[@class="site-main"]/article')
    titles = [
        unescape(getlist1(i.xpath('./header/h2/a/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = [getlist1(i.xpath('.//img/@src')) for i in items]
    urls = [getlist1(i.xpath('./header/h2/a/@href')) for i in items]
    descriptions = [unescape(getlist1(
        i.xpath('./div[@class="entry-content"]/p[1]/text()')).strip()) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':3 * 3600, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_maisui_python(proxy=None):
    # 置顶3小时
    source_name = '麦穗技术'
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://www.58maisui.com/category/python/', proxies=proxy, **default_args)
    items = fromstring(r.text).xpath('//main[@class="site-main"]/article')
    titles = [
        unescape(getlist1(i.xpath('./h3/a/span/text()')).strip()) for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = [getlist1(i.xpath('./h3/a/@href')) for i in items]
    descriptions = [unescape(i.xpath('./div[@class="Article__content"]')
                             [0].text_content().strip().split('\n')[0]) for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':3 * 3600, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_fengyun_python(proxy=None):
    source_name = "峰云's blog"
    time1 = int(time.time())
    level = 3
    r = trequests.get(
        'http://xiaorui.cc/category/python/', proxies=proxy, **default_args)
    # return r.text
    items = fromstring(r.text).cssselect('#mainstay .article')
    titles = [unescape(
        (i.cssselect('.title-article h1 a') or null)[0].text or '').strip() for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = [(i.cssselect('.title-article h1 a') or null)[0].get('href') or ''
            for i in items]
    descriptions = [
        unescape((i.cssselect('.alert-zan') or null)[0].text or '').strip() for i in items]
    result = [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_gitbook_python(proxy=None):
    source_name = 'GitBook'
    time1 = int(time.time())
    level = 3
    result = []
    r = trequests.get(
        'https://www.gitbook.com/explore/topic/python?sort=latest&lang=en', retry=1, proxies=proxy, **default_args)
    items = fromstring(r.content.decode('utf-8')).cssselect('.Books .Book')
    titles = [
        unescape((i.cssselect('.title>a') or null)[0].text or '').strip() for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = [(i.cssselect('.title>a') or null)[
        0].get('href') or '' for i in items]
    descriptions = [unescape(
        (i.cssselect('.description') or null)[0].text or '').strip() for i in items]
    result += [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]

    r = trequests.get(
        'https://www.gitbook.com/explore/topic/python?sort=latest&lang=zh', retry=1, proxies=proxy, **default_args)
    items = fromstring(r.content.decode('utf-8')).cssselect('.Books .Book')
    titles = [
        unescape((i.cssselect('.title>a') or null)[0].text or '').strip() for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = [(i.cssselect('.title>a') or null)[
        0].get('href') or '' for i in items]
    descriptions = [unescape(
        (i.cssselect('.description') or null)[0].text or '').strip() for i in items]
    result += [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]
    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_yus_python(proxy=None):
    source_name = 'Yu’s'
    time1 = int(time.time())
    level = 4
    result = []
    r = trequests.get(
        'http://blog.rainy.im/', retry=1, proxies=proxy, **default_args)
    items = fromstring(r.text).cssselect('#post-list li')
    titles = [unescape(
        (i.cssselect('.entry-title>a') or null)[0].text or '').strip() for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = ['http://blog.rainy.im' +
            ((i.cssselect('.entry-title>a') or null)[0].get('href') or '') for i in items]
    descriptions = [unescape(
        (i.cssselect('.entry-content>p') or null)[0].text or '').strip()[:80] for i in items]
    result += [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]

    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result


def spider_funhacks_python(proxy=None):
    source_name = 'FunHacks'
    time1 = int(time.time())
    level = 3
    result = []
    r = trequests.get(
        'http://funhacks.net/categories/Python/', proxies=proxy, **default_args)
    items = fromstring(r.text).cssselect('.archive-article-header')
    titles = [unescape(
        (i.cssselect('.archive-article-title') or null)[0].text or '').strip() for i in items]
    if '' in titles:
        logit('%s 出现空Title字段。' % source_name)
    covers = ['' for i in items]
    urls = ['https://funhacks.net' +
            ((i.cssselect('.archive-article-title') or null)[0].get('href') or '') for i in items]
    descriptions = [unescape(
        (i.cssselect('.time') or null)[0].text or '').strip() for i in items]
    result += [{'title': i[0], '_id':cleanid(i[0]), 'level':level, 'cover':i[1], 'description':i[2], 'toptime':0, 'urls':{
        source_name: i[3]}, 'time':time1} for i in zip(titles, covers, descriptions, urls)]

    print('%s finished: %s gotten.' % (source_name, len(result)))
    assert len(result) > 0, '%s 抓取结果为 0。' % source_name
    return result

def spider_zhihu_zhuanlan_pythoncoder(proxy=None):
    return  common_zhihu_zhuanlan('pythoncoder','Python开发者社区')

def spider_zhihu_zhuanlan_pythonpx(proxy=None):
    return  common_zhihu_zhuanlan('https://zhuanlan.zhihu.com/api/columns/pythonpx/posts?limit=20&topic=872','通过python学会编程')

def spider_zhihu_zhuanlan_python_cn(proxy=None):
    return  common_zhihu_zhuanlan('https://zhuanlan.zhihu.com/api/columns/python-cn/posts?limit=20&topic=872','Python之美')


def spider_zhihu_zhuanlan_passer(proxy=None):
    return  common_zhihu_zhuanlan('https://zhuanlan.zhihu.com/api/columns/passer/posts?limit=20&topic=872','学习编程')


def auto_retry(func, fail=None, n=2):
    proxy1 = None
    for _ in range(n):
        try:
            result = func(proxy1)
            if result == fail:
                # print('retry',func.__name__)
                time.sleep(5 * _)
                continue
            # print([i['title'] for i in result])
            return result
        except Exception as e:
            # print(func.__name__, e, 'retry', '~~~~~~~~~~~~~~~~~~~~')
            proxy1 = {'http': random.choice(http_local_proxy)}
            continue
    print(func.__name__, 'retry %s times and failed' % n)
    return None
    # try:
    #     return func()
    # except Exception as e:
    #     logit('%s Failed:%s' % (func.__name__, e))
    # return None


def get_all():
    gg = globals()
    async_pool = Async(
        lambda x: auto_retry(x), n=20, timeout=180, timeout_return='')
    funcs = [(gg[i]) for i in gg if i.startswith('spider_')]
    todo = len(funcs)
    funcs = [async_pool(i) for i in funcs]
    results = [i.x for i in funcs if i.x]  # [[dict1,dict2],]
    # results=[i for i in results if i]
    done = len(results)
    print('成功采集数量：%s / %s' % (done, todo))
    # logit('已从 %s 条爬虫中获取数据' % len(results))
    result = sum(results, [])
    for item in result:
        item['datetime'] = ttime(item['time'])
        item['md5'] = md5(item['_id'])
    return result


if __name__ == '__main__':
    # print('请使用其他模块进行调用')
    from pprint import pprint
    test = spider_zhihu_zhuanlan_passer()[:3]
    pprint(test)
    print(schema_check(test))
    # test_schema(test) # 对返回结果的合法性做测试
    # print(globals())
    # print(get_all())

# 普通文章结构：[{'toptime': 0, 'cover':
# 'http://jbcdn2.b0.upaiyun.com/2014/12/6da94dec8f6f96417f14c8291e6345801.png',
# 'description': '使用Python学习selenium测试工具', 'urls': {'伯乐':
# 'http://python.jobbole.com/84477/'}, 'time': 1458298226.2673378,
# 'title': '使用Python学习selenium测试工具'}]
