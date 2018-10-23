# -*- coding: utf-8 -*-
"""
封装一个自己的爬虫类，方便以后的调用
@author: ligantong
"""

from urllib import error
import copy
import random
import time
import sys
import os
import requests 
from myproxy import MyProxy
from myUserAgent import MyUserAgent
import re
from lxml import etree


MAX_WAIT_TIME=1
TRY_MORE_TIME_LIST=[21,50,32,73]
class MySpider:
    """
    调用时可直接调用一个方法，传一个参数，即可对页面进行解析，并
    返回一个列表
    """
    def __init__(self):
        self.proxy=MyProxy()
        self.UserAgent=MyUserAgent()
        self.headers={}
        self.time_list=TRY_MORE_TIME_LIST
#        self.time_list=[1]
    
    def getHtml(self,url,decodeInfo="utf-8",getType="html",num_tries=10,timeout=None):
        """
        支持UA（User-Agent）等Http Request Headers
        支持Proxy
        超时的考虑
        编码的问题，如果不是utf-8怎么办
        服务器错误返回5XX怎么办
        客户端错误返回4XX怎么办
        考虑延时的问题
        """
        time.sleep(MAX_WAIT_TIME*random.random()) #控制访问，不要太过
        
        #获取随机的User-Agent
        headers=copy.deepcopy(self.headers)
        headers.update(self.UserAgent.getUserAgent())
#        print(self.headers)
#        print(headers)
        
        #获取随机代理
        proxies=self.proxy.getProxy()
#        print(proxy)
        
        try:
            response=requests.get(url,headers=headers,proxies=proxies,timeout=timeout)
            response.encoding=decodeInfo      
            #这里可能出现很多异常
            #可能会出现编码异常
            #可能会出现网络下载异常：客户端的异常404,403（很可能已经被发现）
    #                               服务器的异常：5XX
        except UnicodeDecodeError:
            raise UnicodeDecodeError("line50编码错误")    
        except Exception as e:
            #客户端的异常404,403(很可能已经被发现)
            if hasattr(e,"code") and 400<=e.code<500:
                print("Client Error:"+e.code)
            elif hasattr(e,"code") and 500<=e.code<600:
                if num_tries>0:
                    time.sleep(random.choice(self.time_list))
                    self.getHtml(url,
                                 decodeInfo,
                                 getType,
                                 num_tries-1,
                                 timeout)
                if num_tries==0:
                    print("重定向失败："+e.code)
                    return
        except ConnectionError:
            raise ConnectionError("连接主机失败。")
        except Exception as e:
            print(e)
            return
                    
        if getType=="html":
            return response.text
        elif getType=="content":
            return response.content
        
    def postHtml(self,url,decodeInfo="utf-8",getType="html",num_tries=10,timeout=None):
        pass
    
    def parseHtml(self,html,method="xpath",pattern="*"):
        if method=="xpath":
            parsePage=etree.HTML(html)
            r_list=parsePage.xpath(pattern)
        elif method=="re":
            p=re.compile(pattern)
            r_list=p.findall(html)
        else:
            raise TypeError("目前只支持xpath和re两种方法。")
        return r_list
    
    def writeHtml(self,content,filename=None):
        self.filename=filename
        if not self.filename:
            self.filename=os.path.abspath(0)+".txt"
        else:
            self.filename="../"+self.filename
        with open(self.filename,"ab") as f:
            f.write(content)
        
    
    def getList(self,url,pattern):
        html=self.getHtml(url)
        r_list=self.parseHtml(html,pattern=pattern)
        return r_list

        
    def close(self):
        self.proxy.close()
        self.UserAgent.close()
    
    




if __name__=="__main__": 
    spider=MySpider()
    r_list=spider.getList(url="http://www.baidu.com",pattern="//a/@href")
    for r in r_list:
        spider.writeHtml((r+"\n").encode("utf-8"))
    spider.close()  
    
    
    