# /etc/bin/env python
# -*- coding: utf-8 -*-

"""
工控爬虫 V1.0
"""
from lxml import etree
import requests
import sqlite3
import os
import threading

class SqlitConn:
    # 打开数据库
    def open_db(self):

        db_name = os.getcwd() + '\ics.db'
        print(db_name)
        self.db_conn = sqlite3.connect(db_name, check_same_thread = False)
        self.db_cur = self.db_conn.cursor()
        return self.db_cur, self.db_conn

    def close_db(self):

        self.db_conn.commit()
        self.db_conn.close()

def http_num(bash_url):

    r = requests.get(bash_url)
    print(r.status_code, '\n')
    print(r.cookies, '\n')
    r.encoding = 'utf-8'
    req = etree.HTML(r.content)
    max_num = req.xpath('/html/body//div[@class="pages clearfix"]/a[last()-1]/text()')
    max_num = ''.join(max_num)
    print("总共有页码", max_num)
    return  max_num

def sqider(url, db_cur, db_conn, lock):

    r_get = requests.get(url)
    print(r_get.status_code, '\n')
    print(r_get.cookies, '\n')
    r_get.encoding = 'utf-8'
    req_get = etree.HTML(r_get.content)
    # 读取网页信息
    for sel in req_get.xpath('/html/body/div[2]/div/div[2]/table/tbody/tr'):
        name = ''.join(sel.xpath('td/a/@title'))
        level = ''.join(sel.xpath('td[@class]/text()')).strip()
        last_time = ''.join(sel.xpath('td[last()]/text()')).strip()
        blank_url = ''.join(sel.xpath('td/a/@href'))
        sql = 'INSERT INTO ICSBUG (NAME, LEVEL, LAST_TIME, BLANK_URL) VALUES (?, ?, ?, ?)'
        values = (name, level, last_time, blank_url)
        try:
            lock.acquire()
            db_cur.execute(sql, values)
            db_conn.commit()
        finally:
            lock.release()


class MyThread(threading.Thread):

    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)


def main():
    # 打开数据库
    db = SqlitConn()
    db_cur, db_conn = db.open_db()

    threads = []
    bash_url = 'http://ics.cnvd.org.cn/?title=&max=20&offset='
    max_num = http_num(bash_url)
    num = range(0, int(max_num))
    lock = threading.Lock()

    for i in num:
        url = bash_url + str(i * 20)  # 组合完整网址
        t = MyThread(sqider, (url, db_cur, db_conn, lock), sqider.__name__)
        threads.append(t)

    for i in num:
        threads[i].start()

    for i in num:
        threads[i].join()

    db.close_db()

if __name__ == '__main__':

    main()
