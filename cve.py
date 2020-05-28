import csv
import requests
from lxml import etree
import time

'''
批量抓取 CVE 漏洞描述信息。
'''


def  read_file(file):
    
    cve_list = []
    with open(file, newline='') as f:
        read_conn = csv.reader(f, delimiter=' ', quotechar='|')
        for row in read_conn:
            cve_list.append(row[0])
        f.close()
    return cve_list
    
def req_url(cve):
    time.sleep(5)
    url = 'https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword='+cve
    req = requests.get(url)
    res = etree.HTML(req.content)
    req_list = []
    for sel in res.xpath('/html/body/div/div/div[@id="TableWithRules"]/table'):
        cve_id  = ''.join(sel.xpath('tr/td[@nowrap="nowrap"]/a/text()'))
        cve_data = ''.join(sel.xpath('tr/td[last()]/text()'))
        req_list = [cve_id,cve_data]
    
    return req_list

def rw_file(data):
    headers = ['cve_id','data']
    with open('ver.csv','a+',newline='') as f:
        f_csv = csv.DictWriter(f,headers)
        f_csv.writerow({'cve_id':data[0],'data':data[1]})
    f.close()

if __name__ == "__main__":
    
    file = 'version.csv'
    f = read_file(file)
    for i in f:
        req_list = req_url(i)
        print(req_list)
        rw_file(req_list)

    
