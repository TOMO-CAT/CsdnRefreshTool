# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 10:39:39 2019
参考：https://github.com/yooongchun/CSDN_Visitor
@author: TOMOCAT
准备工作：得先构造自己的代理IP池，我已经通过GetProxyIP.py获取，存储在IP.db中
功能：刷csdn博客流量，体验一下互联网pv中的去爬去刷
"""
#from RandomHeaders import FakeHeaders
from DatabaseTable import IPPool, InfoPool
from bs4 import BeautifulSoup
import time
import re
import random
from fake_useragent import UserAgent
import requests
from matplotlib import pyplot as plt #python最常用的可视化工具
from datetime import datetime, timedelta, timezone

class AutoPvUp():
    
    def __init__(self, blogger = "TOMOCAT"):
        self.__RETRY_TIMES = 5
        self.__blogger = blogger
    
    
    def get_proxies(self):
        ##从数据库中随机抽取一行代理IP信息并构建成proxies
        ip  = IPPool("validation_ip_table").select(random_flag = True)
        IP = str(ip[0]) + ":" + str(ip[1])
        return {"http": "http://" + IP}
    
    def get_proxies_2(self):
        ##从数据库中随机抽取一行代理IP信息并构建成proxies
        ##有些网站需要代理是https的形式，暂时不理解为什么
        ip  = IPPool("validation_ip_table").select(random_flag = True)
        IP = str(ip[0]) + ":" + str(ip[1])
        return {"https": "https://" + IP}
    
    def get_referer(self):
        referer_list=[
            'https://blog.csdn.net/TOMOCAT',
            'http://blog.csdn.net/',
            'https://blog.csdn.net/TOMOCAT/article/details/86472537',
            'https://blog.csdn.net/TOMOCAT/article/details/86006806',
            'https://blog.csdn.net/tomocat/article/details/82083357'
        ]
        return random.choice(referer_list)
    
    def parse_to_article_info(self, html):
        #解析html获得文章基本信息
        INFO = []
        soup = BeautifulSoup(html, "lxml")
        try:
            children = soup.find_all(
                "div", {"class", "article-item-box csdn-tracking-statistics"})
        except Exception:
            print("解析html出错!")
            return None
        try:
            for child in children:
                info = {} #构造一个空字典
                info['id'] = child.attrs['data-articleid']
                info['href'] = child.a.attrs['href']
                info['title'] = re.sub(r"\s+|\n+", "", child.a.get_text())
                info['date'] = child.find("span", {"class": "date"}).get_text()
                text = child.find_all("span", {"class": "read-num"})
                info['read_num'] = int(
                    re.findall(r'\d+', text[0].get_text())[0])
                info['commit_num'] = int(
                    re.findall(r"\d+", text[1].get_text())[0])
                INFO.append(info)
        except Exception:
            print("从html中查找文章信息出错!")
            return None
        return INFO
    
    def get_article_info(self):
        #根据博主标识遍历博文列表，并返回博文信息
        page_num = 0
        INFO = []
        while True:
            #因为不清楚博文列表多少页，因此一直跑下去直到无法获取博文信息
            sleep_time = 20 * random.random() #平均10秒的睡眠时间
            print("开始等待{:.1f}秒以避免本地IP受限制...".format(sleep_time))
            time.sleep(sleep_time)
        
            page_num += 1
            #第几页的博文列表
            csdn_url = "https://blog.csdn.net/{}/article/list/{}".format(self.__blogger, page_num)
            print(u"正在访问{}...".format(csdn_url))
            
            #访问次数不多且不频繁，直接爬取信息即可，无需伪造headers
            re_conn_times = 5
            ##因为获取文章信息比较重要，设置重连次数为5，且最终需要返回获取的文章数量
            
            for i in range(re_conn_times):
                try:
                    response = requests.get(url = csdn_url, timeout=5)
                    if response.status_code == 200:
                        break #成功获取response则退出循环
                    else:
                        print(u"response返回结果为:{},等待20秒后重试...".format(
                                response.status_code))
                        time.sleep(20)
                        continue
                except:
                    print(u"访问{}出错!请检查网络状态!".format(csdn_url))
            info = self.parse_to_article_info(response.text)
            #在parse_to_article_info中，解析url出错或者从html中查找文章信息出错都会返回None
            if info is None:
                return None
            if len(info) > 0:
                INFO += info
            else:
                break
        return INFO
    
    def crawl(self, url, headers, proxies):
        #利用爬虫实现通过代理IP访问某个特定的url
        #返回值为True表示正常访问(即code == 200)
        print(u"开始访问博文{}".format(url))
        headers = headers
        proxies = proxies
        code = None #给code赋值防止访问出错时无定义
        
        re_conn_times = 3 #考虑到proxies可能单次不可用，从而多次访问
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
        
    def __gaussian_distribution_random_url(self, info):
        '''
        根据阅读数的高斯分布生成需要访问的博文链接,模拟人类的访问规律
        根据抓取到的info信息生成博文链接和访问概率
        '''
        
        urls = [one['href'] for one in info]
        nums = [int(one['read_num']) for one in info] #提取文章链接和访问量

        #利用阅读数占比生成博文访问概率
        SUM = sum(nums) 
        d = [(url, num) for url, num in zip(urls, nums)] #构建url和num的列表
        d2 = sorted(d, key=lambda x: x[1]) #根据阅读数升序排列
        nums = [one[1] for one in d2]
        urls = [one[0] for one in d2]
        
        probs = [num / SUM for num in nums]#每篇博文访问量占比
        URL_LIST = [(url, prob) for url, prob in  zip(urls, probs)]
        return URL_LIST
        
    def get_gaussian_random_url(self, url_list):
        '''根据带有概率的url列表随机生成url'''
        urls = [one[0] for one in url_list]
        probs = [one[1] for one in url_list]
        P = [sum(probs[0:i + 1]) for i in range(len(probs))] #相当于返回累积概率密度
        r = random.random() #生成随机数
        
        #根据不同的随机数生成对应的url
        if r <= P[0]:
            print(urls[0])
        else:
            for index in range(1,len(P)):
                #print(index)
                if r > P[index - 1] and r <= P[index]:
                    return urls[index]
    
    def csdn_refresh(self, pv_num = 1000, sleeptime = 10):
        '''
        单独刷流量的模块
        pv_num为刷的流量数,sleep为刷访问间隔的时间
        '''
        #获取初始信息
        print(u"正在获取博文信息")
        info = self.get_article_info()
        print(u"生成博文链接列表url_list")
        url_list = self.__gaussian_distribution_random_url(info)
        sleeptime = sleeptime
        #开始刷量
        succ_num = 0
        for i in range(pv_num - 1):
            try:
                proxies = self.get_proxies()
                user_agent = UserAgent().random
                referer = self.get_referer()
                url = self.get_gaussian_random_url(url_list)
                headers = {'User-Agent' : user_agent, 'Referer' : referer}
                succ_flag = self.crawl(url, headers, proxies = proxies)
                if succ_flag:
                    succ_num += 1
                print(u"访问进度{}/{},总成功率{:.2f}%".format(
                        i+1, pv_num, succ_num/(i+1) * 100))
                time.sleep(sleeptime * random.random())
            except:
                continue
        
        try:
            proxies = self.get_proxies()
            user_agent = UserAgent().random
            referer = self.get_referer()
            url = self.get_gaussian_random_url(url_list)
            headers = {'User-Agent' : user_agent, 'Referer' : referer}
            succ_flag = self.crawl(url, headers, proxies = proxies)
            if succ_flag:
                succ_num += 1
            print(u"访问进度{}/{},总成功率{:.2f}%".format(
                    pv_num, pv_num, succ_num/pv_num * 100))
        except:
            pass
        print(u"预定增加pv数为{}，实际增加pv数为{}，访问成功率{:.2f}%".format(
        pv_num, succ_num, succ_num/pv_num * 100))
        
        ##刷量完之后保存数据并可视化博文信息
        print("开始更新并保存博文阅读信息，并可视化访问信息!")
        info = self.get_article_info()
        self.saver(info = info)      ##保存阅读量信息到数据库中
        self.plot(info = info)       ##博文信息可视化
        
    def plot(self, info = None):
        
        if info is None:
            info = self.get_article_info()
        else:
            info = info
        
        print("开始绘制访问信息统计图")
        
        #获取文章阅读数和文章ID列表
        cnt = [one['read_num'] for one in info]
        IDs = [one['id'] for one in info]
        
        '''绘制各文章id对应的阅读数图'''
        plt.style.use('dark_background') ##设置背景主体
        plt.figure(figsize=(30, 20))  ##设置画板
        plt.subplot(211)              ##设置画纸和图片排版
        '''
        subplot()方法传入的三个数字:
        前两个数字代表要生成几行几列的子图矩阵
        最后单个数字代表选中的子图位置
        '''
        plt.bar(range(len(IDs)), cnt)  #绘制条形垂直图
        plt.xticks(range(len(IDs)), IDs)  ##将ID作为刻度标签
        plt.xlabel("Article ID") #中文无法识别
        plt.ylabel("Read Num")
        plt.title("Article ID——Read Num Figure")

        article_info = InfoPool("info_table").select()
        if article_info is None or len(article_info) < 1:
            print("暂无访问量的历史信息，请以后再试!")
        else:
            #当有历史访问量记录时，绘制阅读数和文章数的增长图
            #先获取信息：记录时间、文章数和阅读数列表
            time = [num[0] for num in article_info]        #记录时间列表
            id_num = [int(num[2]) for num in article_info] #记录文章数列表
            num = [int(num[3]) for num in article_info]    #记录阅读数列表

            #绘制文章数增长图
            plt.subplot(223)
            plt.plot(id_num)
            plt.xticks(rotation=60)
            
            #防止条数过多时图形显示冗杂
            cnt = 1
            while len(time) / cnt > 40:
                cnt += 1
            time2 = ["" for i in time]
            time2[0::cnt] = [
                time[index] for index in range(len(time)) if index % cnt == 0
            ]

            plt.xticks(range(len(time2)), time2)
            plt.xlabel("Time")
            plt.ylabel("Article Number")

            plt.subplot(224)
            plt.plot(num)
            plt.xticks(rotation=60)
            plt.xticks(range(len(time2)), time2)
            plt.xlabel("Time")
            plt.ylabel("Read Number")
            plt.savefig("csdn_article_info.png")
            print("保存CSDN博客访问信息图成功!")
            plt.show()
            
    def saver(self, info = None):
        
        print("开始保存文章信息到数据库")
        #判断是否传入info参数
        if info is None:
            info = self.article_info()
        else:
            info = info
    
        total_read_num = sum([one['read_num'] for one in info])
        article_num = len(info)
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc) #世界时间
        bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8))) #转化成北京时间
        INFO = [
                str(bj_dt).split(".")[0],
                time.time(), 
                article_num, 
                total_read_num]
        try:
            InfoPool("info_table").insert([INFO])
            print("保存文章信息到数据库成功!")
            return True
        except:
            print("保存文章信息失败!")
            return False

#设置main函数
if __name__ == "__main__":
    AutoPvUp().csdn_refresh(pv_num = 5000, sleeptime = 8)    
'''测试模块功能
Test = AutoPvUp()
#info = AutoPvUp().get_article_info()
info
Test.saver(info = info)
Test.plot(info = info)
Test.csdn_refresh(pv_num = 10, sleeptime = 10)
'''
