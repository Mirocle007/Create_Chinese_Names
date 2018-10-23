# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 18:55:14 2018

@author: Administrator
"""


#//td[@data-title="匿名度"][contains(.,"匿名")]/ancestor::tr
#
#IP:./td[@data-title="IP"]/text()
#PORT:./td[@data-title="PORT"]/text()

import os
import time
import random
import linecache
import json
import requests
from lxml import etree

#默认为快代理
URL="https://www.kuaidaili.com/ops/proxylist/"
FILENAME="./proxy.txt"
TOTAL_PAGE=10
class MyProxy:
    def __init__(self,url=URL,filename=FILENAME,pages=TOTAL_PAGE):
        self.url=url
        self.filename=filename
        self.pages=pages
        self.headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36"}
        self.proxies={}
        
    #下载网页
    def downloadHtml(self,url):
        res=requests.get(url,headers=self.headers,proxies=self.proxies)
        res.encoding="utf-8"
        return res.text
        
    #解析页面并写入文件,获取IP和端口号，以json格式写入，方便存储和使用
    def parse_writePage(self,html):
        parsepage=etree.HTML(html)
        r_list=parsepage.xpath('//td[@data-title="匿名度"][contains(.,"匿名")]/ancestor::tr')
#        print(r_list)
        if not r_list:
            print("此页没有匿名代理")
            return
        with open(self.filename,"a",encoding="utf-8") as f:            
            for row in r_list:
                data={}
                data["IP"]=row.xpath('./td[@data-title="IP"]/text()')[0].strip()
                data["PORT"]=row.xpath('./td[@data-title="PORT"]/text()')[0].strip()
                data["TYPE"]=row.xpath('./td[@data-title="类型"]/text()')[0].strip()
                data=json.dumps(data)
                f.write(data)
                f.write("\n")
                
    
    #爬取代理
    def workOn(self):
        for page in range(self.pages):
            url=self.url+str(page+1)+"/"
            html=self.downloadHtml(url)
            self.parse_writePage(html)
            print(url+"爬取成功.")
            time.sleep(random.randint(1,3))
        print("爬取完成。")
            
    
    #从文件中随机选取一个代理
    def getProxy(self):
        if not os.path.exists(self.filename):
            self.workOn()
        IP_PORT=None
        while not IP_PORT:
            line=random.randint(1,100)        
            IP_PORT = linecache.getline(FILENAME,line).strip()
        IP_PORT=json.loads(IP_PORT)
        IP=IP_PORT["IP"]
        PORT=IP_PORT["PORT"]
        proxies={"HTTP":IP+":"+PORT}
        return proxies
    
    def close(self):
        linecache.clearcache()
        

if __name__=="__main__":
    myproxy=MyProxy()
#    myproxy.workOn()
    proxies=myproxy.getProxy()
    print(proxies)   
    myproxy.close()

    
    