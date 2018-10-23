# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 15:22:08 2018

@author: ligantong
"""

import os
from mySpider import *

class NameSpider(MySpider):
    base_url="http://www.resgain.net/xmdq.html"
    
    def writeHtml(self,r_list,filename=None):
        if not r_list:
            return        
        self.filename=filename
        if not self.filename:
            self.filename=os.path.abspath(0)+".txt"
        with open(self.filename,"at") as f:
            for r in r_list:
                f.write(r.strip()+"\n")

if __name__=="__main__":
    spider=NameSpider()
    html1=spider.getHtml(spider.base_url)
    pattern1="//a[@class='btn btn2']/@href"
    pattern2="//a[@class='btn btn-link']/text()"
    r_list1=spider.parseHtml(html1,method="xpath",pattern=pattern1)
    for r in r_list1:
        for page in range(1,11):
            url="http:"+r[:-5]+"_"+str(page)+".html"
            html2=spider.getHtml(url)
            r_list2=spider.parseHtml(html2,method="xpath",pattern=pattern2)
            spider.writeHtml(r_list2,filename="name.txt")
        print("下载完成"+r)

        

    
    