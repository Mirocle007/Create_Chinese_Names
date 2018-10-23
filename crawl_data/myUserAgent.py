# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 20:37:49 2018

@author: ligantong
"""
import sys
import os
import linecache
import random

FILENAME="./useragent.txt"
LINES=40

class MyUserAgent:
    def __init__(self):
        if not os.path.exists(FILENAME):
            sys.exit(FILENAME+"文件不存在")
#            raise FILENAME+"文件不存在"
    
    def getUserAgent(self):
        user_agent=None
        while not user_agent:
            line=random.randint(1,LINES)        
            user_agent=linecache.getline(FILENAME,line).strip()
        return {"User-Agent":user_agent}
    
    def close(self):
        linecache.clearcache()
    

if __name__=="__main__":
    myuseragent=MyUserAgent()
    user_agent=myuseragent.getUserAgent()
    print(user_agent)
    myuseragent.close()