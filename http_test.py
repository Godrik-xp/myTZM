#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
from BeautifulSoup import BeautifulSoup
from datetime import datetime
import socket
import threading
import time


try:
    def keysend():
        global isthreadsrunning
        isthreadsrunning += 1 
        print u'[%s] Отправка 1000 команд… Поток: %s' % ( datetime.now(), isthreadsrunning )
        start = datetime.now()
        for i in range(1000):
            try:
                result = urllib2.urlopen(URL + 'sync/' + sync_block_id + '/?sid=' + sid, 'key=-D').read()
                time.sleep(.01)
            except urllib2.HTTPError, e:
                #print e.read()
                pass

        time_diff = datetime.now() - start
        print u'[%s] Время отправки: %s' % (datetime.now(), time_diff.total_seconds())
        isthreadsrunning -= 1 
        
    def keyread():
        global isthreadsrunning
        isthreadsrunning += 1 
        print u'[%s] Чтение 1000 записей… Поток: %s' % ( datetime.now(), isthreadsrunning )
        start = datetime.now()
        for i in range(1000):
            try:
                result = urllib2.urlopen(URL + 'sync/' + sync_block_id + '/?sid=' + sid).read()
                time.sleep(.01)
            except urllib2.HTTPError, e:
                #print e.read()
                pass

        time_diff = datetime.now() - start
        print u'[%s] Время чтения: %s' % (datetime.now(), time_diff.total_seconds())
        isthreadsrunning -= 1 

    isthreadsrunning = 0

    URL = 'http://127.0.0.1:8000/trainer/'

    print u'[%s] Вход в систему…' % datetime.now()
    data = urllib2.urlopen(URL + 'login/?username=test&password=test').read()
    sid = BeautifulSoup(data).find('user')['sid']
    print u'[%s] Идентификатор сессии: %s' % (datetime.now(), sid)

    print u'[%s] Создание блока синхронизации…' % datetime.now()
    sync_block_id = urllib2.urlopen(URL + 'start_sync/1/1/?sid=' + sid).read()
    print '[%s] Идентификатор блока синхронизации: %s' % (datetime.now(), sync_block_id)

    threading.Thread(target=keysend).start()
    threading.Thread(target=keysend).start()
    threading.Thread(target=keyread).start()
    threading.Thread(target=keyread).start()
    threading.Thread(target=keyread).start()
    
    while isthreadsrunning:
        time.sleep(1)

    print u'[%s] Конец блока синхронизации.' % datetime.now()
    urllib2.urlopen(URL + 'end_sync/' + sync_block_id + '/?sid=' + sid)

    print u'[%s] Выход из системы.' % datetime.now()
    data = urllib2.urlopen(URL + 'logout/?sid=' + sid)
except KeyboardInterrupt:
    print u'[%s] Прервано пользователем.' % datetime.now()
except urllib2.URLError:
    print u'[%s] Нет соединения с сервером.' % datetime.now()
except socket.error:
    print u'[%s] Потеряно соединение с сервером.' % datetime.now()

