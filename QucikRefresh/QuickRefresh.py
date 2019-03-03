# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 14:28:17 2019

@author: YANG
"""

from IncreaseCsdnPv import AutoPvUp
import json #json即字典型的字符串
import sys
import ast
from fake_useragent import UserAgent
import time
import random
from bs4 import BeautifulSoup

#定期获取INFO存储到INFO.txt中，防止刷量导致登录才能获取博文信息
#INFO = AutoPvUp().get_article_info()
def text_save(filename, data):#filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename,'a')
    for i in range(len(data)):
        s = str(data[i]).replace('[','').replace(']','')#去除[],这两行按数据不同，可以选择
        s = s+'\n'   #去除单引号，逗号，每行末尾追加换行符
        file.write(s)
    file.close()
    print("保存文件成功") 
#text_save('C:\\Users\\YANG\\Desktop\\CSDN_Visit\\INFO.txt', INFO)

#读取txt中的数据并保存为list
def get_newest_article_info():
    article_info = []
    with open('C:\\Users\\YANG\\Desktop\\CSDN_Visit\\INFO.txt','r') as f:
        for line in f:
            #print(line.strip('\n')) #字典
            line = ast.literal_eval(line) #将txt中str类型的行转化为dict类型
            article_info.append(line)
    return article_info
        
def total_url_finish(blog_link):
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

def refresh(pv_each_article = 1):
    #设置希望每篇文章增加的pv数
    
    #前期准备
    info = get_newest_article_info() 
    blog_link = [one['href'] for one in info]
    blog_num = len(blog_link)
    
    total_succ_num = 0
    
    for i in range(pv_each_article):
        #循环n次
        succ_num = total_url_finish(blog_link = blog_link)
        total_succ_num += succ_num
    
    
    print(u"预计刷量{},实际访问成功{}".format(
            pv_each_article * blog_num, total_succ_num))
    
if __name__ == "__main__":
    print("每篇文章增加100访问量")
    refresh(pv_each_article = 100)

