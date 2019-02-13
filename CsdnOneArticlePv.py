# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 01:04:15 2019

@author: YANG
"""

from RandomHeaders import FakeHeaders
from DatabaseTable import IPPool
import time
import re
import random
from fake_useragent import UserAgent
import requests

def get_proxies():
    ##从数据库中随机抽取一行代理IP信息并构建成proxies
    ##有些网站需要代理是https的形式，暂时不理解为什么
    ip  = IPPool("validation_ip_table").select(random_flag = True)
    IP = str(ip[0]) + ":" + str(ip[1])
    return {"http": "http://" + IP}

def crawl(url, headers, proxies):
    #利用爬虫实现通过代理IP访问某个特定的url
    #返回值为True表示正常访问(即code == 200)
    print(u"开始访问博文{}".format(url))
    headers = headers
    proxies = proxies
    code = None #给code赋值防止访问出错时无定义
    
    re_conn_times = 3 #考虑到proxies可能不可用，从而多次访问
    for i in range(re_conn_times):
        
        try:
            code = requests.get(url=url, headers=headers, proxies=proxies, timeout=5).status_code
            if int(code) == 200:
                break #返回200时跳出循环
        except Exception:
            continue #无法正常访问时继续重试
    
    if code is None :
        print(u"访问{}出错!请检查网络状态!".format(url, code))
        return False
    
    if int(code) == 200:
        print(u"访问{}成功!".format(url))
        return True
    
    else:
        print(u"无法正常访问{},返回code值为{}!".format(url, code))
        return False

pv_num = 50 #设置访问次数
url = 'https://blog.csdn.net/TOMOCAT/article/details/81145496' #设置待访问url
succ_num = 0

for i in range(pv_num - 1):
    try:
        proxies = get_proxies()
        user_agent = UserAgent().random
        referer = 'https://blog.csdn.net/TOMOCAT'
        headers = {'User-Agent' : user_agent, 'Referer' : referer}
        succ_flag = crawl(url, headers, proxies = proxies)
        if succ_flag:
            succ_num += 1
        print("开始等待60秒防止反爬策略识别...")
        time.sleep(60)
    except:
        continue
try:
    proxies = get_proxies()
    user_agent = UserAgent().random
    referer = 'https://blog.csdn.net/TOMOCAT'
    headers = {'User-Agent' : user_agent, 'Referer' : referer}
    succ_flag = crawl(url, headers, proxies = proxies)
    if succ_flag:
        succ_num += 1
except:
    pass        
print(u"预定增加pv数为{}，实际增加pv数为{}，访问成功率{:.2f}%".format(
        pv_num, succ_num, succ_num/pv_num * 100))