# /etc/bin/env python
# -*- coding: utf-8 -*-

"""
spider v 0.1
www.cnvd.org.cn 网站工控漏洞爬虫

"""
from selenium import webdriver
from lxml import etree
import requests
import time
import sqlite3
import csv
import os


class SqlitConn:
    # 打开数据库
    def open_db(self):

        db_name = os.getcwd() + '/ics.db'
        self.db_conn = sqlite3.connect(db_name)
        self.db_cur = self.db_conn.cursor()
        return self.db_cur

    def update_db(self):
        self.db_conn.commit()

    def close_db(self):
        self.db_conn.commit()
        self.db_conn.close()


def GetCookies(url='http://www.cnvd.org.cn/'):
    # 获取网站COOKie
    browser = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(firefox_options=browser)
    driver.get(url)
    conn = ";".join([item["name"] + "=" + item["value"] for item in driver.get_cookies()])
    time.sleep(2)
    driver.quit()
    return conn

def Get_URL(url):
    # 访问网站 获取网页信息
    global cnvd_cookie
    try:
        header = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/65.0.3325.181 Safari/537.36"}
        r = requests.get(url, headers=header)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            time.sleep(5)
            cnvd_cookie = GetCookies()
            r = requests.get(url, headers=header)
            r.encoding = 'utf-8'
            req = etree.HTML(r.content)
            print(req)
            return req
        else:
            req = etree.HTML(r.content)
            return req
    except Exception as e:
        print('GetURLError:%s;Reason:%s' % (url, e))

def spider(url):
    # 提权网页信息
    req = Get_URL(url)
    items = req.xpath('/html/body//div[@class="tableDiv"]/table/tbody/tr')
    cnvd_cveid = 0
    for item in items:

        cnvd_title = ''.join(item.xpath('td[@class="alignRight"]/text()')).strip()
        cnvd_text = ''.join(item.xpath('td[last()]/text()')).strip()

        if cnvd_title == 'CNVD-ID':
            cnvd_id = cnvd_text

        elif cnvd_title == '公开日期':
            cnvd_time = cnvd_text

        elif cnvd_title == '危害级别':
            cnvd_level = ''.join(cnvd_text.split()).replace('()', '')

        elif cnvd_title == '影响产品':
            cnvd_impact = ''.join(cnvd_text.split())

        elif cnvd_title == 'CVE ID':
            cnvd_text = ''.join(item.xpath('td/a/text()')).strip()
            cnvd_cveid = cnvd_text

        elif cnvd_title == 'BUGTRAQ ID':
            cnvd_text = ''.join(item.xpath('td/a/text()')).strip()
            cnvd_cveid = cnvd_text

        elif cnvd_title == '漏洞描述':
            cnvd_describe = ''.join(cnvd_text.split())

        elif cnvd_title == '参考链接':
            cnvd_reference = ''.join(item.xpath('td/a/text()')).strip()

        elif cnvd_title == '漏洞解决方案':
            cnvd_solution = ''.join(cnvd_text.split())

        elif cnvd_title == '厂商补丁':
            cnvd_text = ''.join(item.xpath('td/a/text()')).strip()
            cnvd_patch = cnvd_text

        elif cnvd_title == '更新时间':
            cnvd_update = cnvd_text

        else:
            print('')
    # 写入csv文件
    try:
        values = [cnvd_id, cnvd_time, cnvd_level, cnvd_impact, cnvd_cveid, cnvd_describe,
                  cnvd_reference, cnvd_solution, cnvd_patch, cnvd_update]

        with open('test.csv', 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(values)
    except Exception as e:
        print('GetURLError:%s;Reason:%s' % (url, e))

if __name__ == '__main__':

    db = SqlitConn()
    cur = db.open_db()
    url = cur.execute('SELECT {} FROM ICSBUG '.format('BLANK_URL'))
    cook = GetCookies()
    for i in url:
        http_url = ''.join(i)
        print(http_url)
        spider(http_url)

    db.close_db()





