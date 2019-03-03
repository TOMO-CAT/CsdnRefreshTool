### 功能
网址 "https://blog.csdn.net/{}/article/list/{}" 在刷量频繁的时候必须登录才能访问，从而QuickRefresh定期保存博文信息到本地文件"INFO.txt"中。

### 问题
当设置的sleeptime系数(即平均两次博文访问的休眠时长为sleeptime * 2)较小时，CSDN仍然会开启登录验证，否则无法访问博文。
![登录限制](https://github.com/TOMO-CAT/CsdnRefreshTool/blob/master/QucikRefresh/error.png)
#### 1. sleeptime系数试错
|sleeptime参数|是否开启登录限制|
|-|-|
|2.5|是|
|...|...|

#### 2.问题描述
* 开启登录限制后用本地浏览器在未登录的情况下无法访问自己的博文
* 开启登录限制后用本地浏览器在未登录的情况下无法访问他人的CSDN博文
* 手机端非登录情况下能正常访问他人的CSDN博文
* 用同个无线下的其他电脑也无法访问他人的CSDN博文
* 本机登录情况下也能正常访问他人CSDN博文
* 同时间段他人的电脑能正常访问CSDN博文

#### 3.后续解决方案
暂时还未处理
