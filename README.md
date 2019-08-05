# CsdnRefreshTool
> 由于时间久远，加上代码质量不佳，暂废弃，最近会升级为可维护性较高的CsdnRefreshTool2.0版本。
以CSDN为例利用爬虫实现刷PV流量
## 理解PV与UV
常见的网页分析或者APP用户行为分析中，PV和UV都是常见的指标。其中PV指Page View（即页面加载的次数），UV指Unique View（即访问页面的自然人）。一般PV都大于UV。
由于PV是数据分析师进行统计分析的重要指标，因此对于一些非自然访问（包括爬虫）的PV要进行限制。**Google Analytics将PV与session绑定在了一起，其中session指用户在一次在网站进行活动的过程，一般认为会话结束有三种方式**：

* 用户关闭了该网站
* 用户距离上次活动超过了30分钟
* 所在地区的24:00点

>通过session跟踪的PV更加具有统计意义，也能在一定程度上去爬去刷带来的PV增长，更有助于分析PV的商业价值。


UV指的是访问的用户数。系统为每个访问的用户自动匹配一个唯一标识符。在网页上，该标识符存储于浏览器的Cookie中。**但是一个用户用两个浏览器打开同个页面算两个UV，在同个浏览器清除Cookie再访问相同页面也算两个UV**。
## 网站防止刷量的方法
当网站反爬反刷的策略我们了然于胸时，准确高效地刷量也就容易了，具体的就不展开讲了。网站防止刷量的方法有：

* 频率监控：对于同一IP，在短时间段内访问次数超过某个阈值时会封禁该IP
* 频数监控：对同一用户访问页面的数量进行控制，如果访问次数过多对其进行限制
*  Headers识别：一般指UA和Referer的限制，用于判断是否是真实的用户在进行访问。其中UA包含用户操作系统和浏览器的信息、Referer指来源链接。
* 统计PV的规则：即使更换不同的IP，两个不同的IP间隔访问时间超过某个阈值才会统计成两个PV。**对于一个特定的URL暂时没有好的解决方法，但是可以设置睡眠时间和URL列表从而实现不间断刷量**。
* 访问规律：当你博文的访问量过高时，如果访问存在很强的规律性（例如短期内均匀快速增长和昼夜增长速度一致），很容易被识别成刷量。一方面可以模拟人类行为行为，另一方面刷量不可太高。

## 开发思路
### 1、获取CSDN博文信息
在开始刷CSDN博文浏览量之前，我们先要拿到所有博文的链接和其他信息。正好CSDN的博文存储在形如 "https://blog.csdn.net/{}/article/list/{}" 的链接（第一个{}是你的CSDN用户标识，第二个{}从1开始表示你的博文列表页）。具体的实现如下:

```
def get_article_info(self):
    #根据博主标识遍历博文列表，并返回博文信息
    page_num = 0
    INFO = []
    sleep_time = 1 + 4 * random.random() #1~5秒的睡眠时间
    while True:
        #因为不清楚博文列表多少页，因此一直跑下去直到无法获取博文信息
        time.sleep(sleep_time)
        page_num += 1
        #第几页的博文列表
        csdn_url = "https://blog.csdn.net/{}/article/list/{}".format(self.__blogger, page_num)
        print(u"正在访问{}...".format(csdn_url))

        headers = FakeHeaders().random_headers_for_csdn()
        re_conn_times = 5
        ##因为获取文章信息比较重要，设置重连次数为5，且最终需要返回获取的文章数量

        for i in range(re_conn_times):
            try:
                response = requests.get(url = csdn_url, headers=headers, timeout=5)
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
```
### 2、刷量核心代码
当执行一次`requests.get()`方法则相当于浏览器打开一次链接，访问量+1。但是由于单个IP访问次数过多或者过频繁，容易被封IP；使用随机的UA和Referer构造headers模拟浏览器登陆。
```
requests.get(url=url, headers=headers, proxies=proxies, timeout=5)
```
### 3、根据浏览量构建高斯分布的url链接模拟人类访问行为
理论上阅读数更高的博文阅读数增长速度也就越快，为了刷量的合理性，我们根据浏览量的分布特征构建随机生成url的函数。其中`__gaussian_distribution_random_url()`生成每个博文链接对应的概率；`get_gaussian_random_url()`用于获取随机博文链接。
```
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
```
## 包含的模块
### 1、DatabaseTable.py
提供了数据库支持，包括建表和增删查改操作。主要包括`IPPool()`（之前储存的爬虫代理IP数据库）和`InfoPool()`（存储不同时间点的博文数和博文阅读数，用于检验刷量结果）。
```
from DatabaseTable import IPPool, InfoPool
```
>关于如何获取代理IP池和对代理IP有效性进行检验，可以查看[https://github.com/TOMO-CAT/ProxyIPPool](https://github.com/TOMO-CAT/ProxyIPPool)

### 2、RandomHeaders.py
返回随机的headers，用于伪造浏览器访问。
```
from RandomHeaders import FakeHeaders
```
### 3、CsdnOneArticlePv.py
根据提供的博文列表刷单独某一篇CSDN文章的阅读量。因为访问太频繁的话阅读量不会增加，所以每次访问完之后就停顿一分钟。
```
#修改CsdnOneArticlePv.py 中的url
python CsdnOneArticlePv.py
```
### 4、IncreaseCsdnPv.py
核心代码，遍历博文列表后模拟历史阅读量规律进行刷量。有几个函数可以在不同情况下调用实现不同的功能

* 保存当前的博文数和阅读量数据到数据库中

```
from IncreaseCsdnPv import AutoPvUp
AutoPvUp().saver()
```

* 博文阅读量信息可视化

```
from IncreaseCsdnPv import AutoPvUp
AutoPvUp().plot()
```
![](https://github.com/TOMO-CAT/CsdnRefreshTool/blob/master/csdn_article_info.png)
>最上面的图是不同文章的阅读量数据；左下角的图是文章数增长图；右下角的图是阅读量增长图。

* 根据提供的刷量pv_num和睡眠时间sleeptime启动刷量程序

```
from IncreaseCsdnPv import AutoPvUp
AutoPvUp().csdn_refresh(pv_num = 1000, sleeptime = 10)
```
### 5、FastRefresh.py
相对独立的模块，和IncreaseCsdnPv.py模仿博文访问数的高斯分布进行访问不同，FastRefresh模块每次遍历访问所有博文一次，同时缩短了两次访问的休眠时间，实现了更快的刷量速度。
但是需要慎用，在我实际的使用过程中经常因为速度过快导致requests结果出错。

## 参考
https://blog.csdn.net/dala_da/article/details/79401163
https://github.com/yooongchun/CSDN_Visitor
https://blog.csdn.net/topleeyap/article/details/79119098
