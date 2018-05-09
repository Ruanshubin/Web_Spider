> 在很多机器学习应用中，天气数据为重要的辅助特征数据，故本文主要介绍如何利用Python获取历史天气数据。

## 目标网站

数据爬取的目标网站为[天气网](http://lishi.tianqi.com/)

![目标网站](http://p3f66obex.bkt.clouddn.com/16-1.JPG)

## 编程实现

### 导入相关包

```
import requests  # 导入requests
from bs4 import BeautifulSoup  # 导入bs4中的BeautifulSoup
import os
import re
import csv
import pandas as pd
import numpy as np
import time
import json
```

> 下面以爬取北京市历史天气数据为例进行演示：

### 获取所有月份URL

分析网页源代码可知，所有月份的URL在'tqtongji1'的div中。

![get_url](http://p3f66obex.bkt.clouddn.com/16-2.JPG)

实现代码如下：

```
def get_url(request_url):
    html = requests.get(request_url).text
    Soup = BeautifulSoup(html, 'lxml') # 解析文档
    all_li = Soup.find('div', class_='tqtongji1').find_all('li')
    url_list = []
    for li in all_li:
        url_list.append([li.get_text(), li.find('a')['href']])       
    return url_list
```

### 获取某月份的历史天气数据

获取到月份URL后，分析月份的页面源代码可知，历史天气数据在'tqtongji2'的div中。

![month_data](http://p3f66obex.bkt.clouddn.com/16-3.JPG)

源代码如下：

```
def get_month_weather(year_number, month_number):
    # month_url = 'http://lishi.tianqi.com/beijing/201712.html'
    url_list = get_url(request_url)
    for i in range(len(url_list)-1, -1, -1):
        year_split = int(url_list[i][0].encode('utf-8')[:4])
        month_split = int(url_list[i][0].encode('utf-8')[7:9])
        if year_split == year_number and month_split == month_number:
            month_url = url_list[i][1]
    html = requests.get(month_url).text
    Soup = BeautifulSoup(html, 'lxml') # 解析文档
    all_ul = Soup.find('div', class_='tqtongji2').find_all('ul')
    month_weather = []
    for i in range(1, len(all_ul)):
        ul = all_ul[i]
        li_list = []
        for li in ul.find_all('li'):
            li_list.append(li.get_text().encode('utf-8'))
        month_weather.append(li_list)
    return month_weather
```

### 获取某年的历史天气数据

获取某年的数据与获取某月的数据类似，即将年份的所有月份的URL提取出来，然后进行访问。

源代码如下：

```
def get_year_weather(request_url, year_number): # year_number
    year_weather = []
    url_list = get_url(request_url)
    year_list = []
    # 获取年份year_number的url列表
    for i in range(len(url_list)-1, -1, -1):
        year_split = int(url_list[i][0].encode('utf-8')[:4])
        if year_split == year_number:
            year_list.append(url_list[i])
    for i in range(len(year_list)):
        month_url = year_list[i][1]
        month_weather = get_month_weather(month_url)
        year_weather.extend(month_weather)
        print '第%d月天气数据采集完成，望您知悉！'%(i+1)
    col_name = ['Date', 'Max_Tem', 'Min_Tem', 'Weather', 'Wind', 'Wind_Level']
    result_df = pd.DataFrame(year_weather)
    result_df.columns = col_name
    # result_df.to_csv('year_weather.csv')
    return result_df
```

执行'result_df = get_year_weather(request_url, 2017)'，结果如下：

![year_data](http://p3f66obex.bkt.clouddn.com/16-4.JPG)







