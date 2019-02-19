# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 15:17:24 2019

@author: YANG
功能：实现快速提升访问量
"""
from IncreaseCsdnPv import AutoPvUp
from fake_useragent import UserAgent
import time
import random

class amazing_fast(object):
    
    def total_url_finish(self, blog_link):
        #所有博文链接访问一次,返回访问成功数
        
        succ_num = 0 #初始化成功次数
        #循环访问博文实现访问数+1  
        
        for url in blog_link:
            proxies = AutoPvUp().get_proxies()
            user_agent = UserAgent().random    
            referer = AutoPvUp().get_referer()
            headers = {'User-Agent' : user_agent, 'Referer' : referer}
            try:
                succ_flag = AutoPvUp().crawl(url, headers, proxies = proxies)
                if succ_flag:
                    succ_num += 1
            except: 
                continue
            
            time.sleep(4 * random.random())  #平均休眠两秒防止访问过于密集
                
        blog_num = len(blog_link)
        print(u"访问成功数{}，总博文数{}，访问成功率{:.2f}%".format(
                succ_num, blog_num, succ_num / blog_num * 100))
        
        return succ_num #返回每轮成功的访问数
    
    def refresh(self, pv_each_article = 1):
        #设置希望每篇文章增加的pv数
        
        #前期准备
        info = AutoPvUp().get_article_info()  
        blog_link = [one['href'] for one in info]
        blog_num = len(blog_link)
        read_num = [int(one['read_num']) for one in info]
        total_read_num_before = sum(read_num) #刷量之前的总访问量
        
        total_succ_num = 0
        
        for i in range(pv_each_article):
            #循环n次
            succ_num = self.total_url_finish(blog_link = blog_link)
            total_succ_num += succ_num
        
        info = AutoPvUp().get_article_info()   
        total_read_num_after = sum([int(one['read_num']) for one in info])
        
        print(u"访问量由{}增长为{}".format(total_read_num_before, total_read_num_after))
        print(u"预计刷量{},实际访问成功{},最终实际访问量增长{}".format(
                pv_each_article * blog_num, total_succ_num, total_read_num_after - total_read_num_before))
        
'''测试模块功能
Test = amazing_fast()
Test.refresh(pv_each_article = 2)
'''

'''
有两个神奇的小问题：
（1）自己登陆后查看的访问量要高于爬虫得到的访问量
（2）博文列表俩民出现了其他作者的链接
https://blog.csdn.net/yoyo_liyy/article/details/82762601
'''
