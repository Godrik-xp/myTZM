#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import socket
from datetime import datetime
from BeautifulSoup import BeautifulSoup

ERRORCOUNT = 0

def httpquery(text, url, post=None, waitcode=200):
    global ERRORCOUNT
    data = None
    start = datetime.now()
    print u'[%s] Начало выполнения: "%s" url: %s' % (datetime.now(), text, url)
    time_diff = datetime.now() - start
    try:
        data = urllib2.urlopen(url, post).read()
        if data:
            print u'[%s] Результат:' % datetime.now()
            print data
    except urllib2.HTTPError, e:
        print u'[%s] Завершение с исключением (http status code %s)' % (datetime.now(), e.code)
        if waitcode != e.code: ERRORCOUNT += 1
    else:
        print u'[%s] Нормальное завершение' % datetime.now()

    print u'[%s] Окончание выполнения: "%s"' % (datetime.now(), text)
    print u'[%s] Время выполение "%s": %s' % (datetime.now(), text, time_diff.total_seconds())
    print
    return data

URL = 'http://127.0.0.1:8000/trainer/'

try:
    data = httpquery(u'Ошибочные логин', URL + 'login/?username=test&password=oops')
    data = httpquery(u'Выход без логина', URL + 'logout/', waitcode=401)

    data = httpquery(u'Верный логин', URL + 'login/?username=test&password=test')
    sid = BeautifulSoup(data).find('user')['sid']
    data = httpquery(u'Выход', URL + 'logout/?sid=' + sid)

    #login для дальнейших тестов    
    data = urllib2.urlopen(URL + 'login/?username=test&password=test').read()
    sid = BeautifulSoup(data).find('user')['sid']

    sync_block_id = httpquery(u'Создать блок синхронизации', URL + 'start_sync/1/1/?sid=' + sid)
    httpquery(u'Создать блок синхронизации (без логина)', URL + 'start_sync/1/1/', waitcode=401)
    httpquery(u'Создать блок синхронизации (для несуществующего модуля)', URL + 'start_sync/100000000000000/1/?sid=' + sid, waitcode=404)

    sync_id = httpquery(u'Записать в блок синхронизации', URL + 'sync/' + sync_block_id + '/?sid=' + sid, 'key=-D')
    for i in range(10):
        httpquery(u'Записать в блок синхронизации (%s из 10)' % i, URL + 'sync/' + sync_block_id + '/?sid=' + sid, 'key=-D')
    httpquery(u'Записать в блок синхронизации (для несуществующего блока)', URL + 'sync/99999999/?sid=' + sid, 'key=-D', waitcode=404)
    httpquery(u'Записать в блок синхронизации (без логина)', URL + 'sync/' + sync_block_id + '/', 'key=-D', waitcode=401)

    httpquery(u'Прочитать блок синхронизации', URL + 'sync/' + sync_block_id + '/?sid=' + sid)
    httpquery(u'Прочитать блок синхронизации (относительно указанного id)', URL + 'sync/' + sync_block_id + '/?sid=' + sid + '&id=' + sync_id)
    httpquery(u'Прочитать блок синхронизации (без логина)', URL + 'sync/' + sync_block_id + '/', waitcode=401)
    httpquery(u'Прочитать блок синхронизации (для несуществующего блока)', URL + 'sync/99999999/?sid=' + sid, waitcode=404)

    httpquery(u'Закрыть блок синхронизации (для несуществующего блока)', URL + 'end_sync/9999999999/?sid=' + sid, waitcode=404)
    httpquery(u'Закрыть блок синхронизации (без логина)', URL + 'end_sync/' + sync_block_id + '/', waitcode=401)
    httpquery(u'Закрыть блок синхронизации', URL + 'end_sync/' + sync_block_id + '/?sid=' + sid)
    httpquery(u'Закрыть еще раз блок синхронизации', URL + 'end_sync/' + sync_block_id + '/?sid=' + sid)
except KeyboardInterrupt:
    print u'[%s] Прервано пользователем.' % datetime.now()
except urllib2.URLError:
    print u'[%s] Нет соединения с сервером.' % datetime.now()
except socket.error:
    print u'[%s] Потеряно соединение с сервером.' % datetime.now()
    
print "Число неожиданных кодов сервера: %s" % ERRORCOUNT
