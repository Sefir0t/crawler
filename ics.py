# /etc/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫
"""
import requests
import sqlite3
import os
from lxml import etree
import threading


class SqlitConn:
    # 打开数据库
    def open_db(self):

        db_name = os.getcwd() + '/ics.db'
        print(db_name)
        self.db_conn = sqlite3.connect(db_name)
        self.db_cur = self.db_conn.cursor()
        return self.db_cur

    def close_db(self):

        self.db_conn.commit()
        self.db_conn.close()

def http():

    bash_url = 'http://ics.cnvd.org.cn/?title=&max=20&offset='

    r = requests.get(bash_url)
    print(r.status_code, '\n')
    print(r.cookies, '\n')
    r.encoding = 'utf-8'
    req = etree.HTML(r.content)
    max_num = req.xpath('/html/body//div[@class="pages clearfix"]/a[last()-1]/text()')
    max_num = ''.join(max_num)
    print("总共有页码", max_num)


    t = MyThread(bash_url, max_num)
    t.start()

def sqider(bash_url, max_num):


    db = SqlitConn()
    db_cur = db.open_db()

    for i in range(0, int(max_num)):

        url = bash_url + str(i * 20)  # 组合完整网址
        r_get = requests.get(url)
        print(r_get.status_code, '\n')
        print(r_get.cookies, '\n')
        r_get.encoding = 'utf-8'
        req_get = etree.HTML(r_get.content)
        for sel in req_get.xpath('/html/body/div[2]/div/div[2]/table/tbody/tr'):
            name = ''.join(sel.xpath('td/a/@title'))
            level = ''.join(sel.xpath('td[@class]/text()')).strip()
            last_time = ''.join(sel.xpath('td[last()]/text()')).strip()
            blank_url = ''.join(sel.xpath('td/a/@href'))
            sql = 'INSERT INTO ICSBUG (NAME, LEVEL, LAST_TIME, BLANK_URL) VALUES (?, ?, ?, ?)'
            values = (name, level, last_time, blank_url)
            db_cur.execute(sql, values)

    db.close_db()

class MyThread(threading.Thread):

    def __init__(self, bash_url, max_num):
        threading.Thread.__init__(self)
        self.bash_url = bash_url
        self.max_num = max_num

    def run(self):
        sqider(self.bash_url, self.max_num)

if __name__ == '__main__':

    http()
