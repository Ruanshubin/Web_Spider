# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 15:41:56 2018

@author: JiaoTong
"""

# 通过Python获取历史天气
import requests  #导入requests
from bs4 import BeautifulSoup  #导入bs4中的BeautifulSoup
import os
import re
import csv
import pandas as pd
import numpy as np
import time
import json

class get_history_weather():
    def __init__(self):
        self.request_url = 'http://lishi.tianqi.com/beijing/index.html'
    
    def get_url(self):
        # 获取所有月份的url
        html = requests.get(self.request_url).text
        Soup = BeautifulSoup(html, 'lxml') # 解析文档
        all_li = Soup.find('div', class_='tqtongji1').find_all('li')
        url_list = []
        for li in all_li:
            url_list.append([li.get_text(), li.find('a')['href']])       
        return url_list
     
    def get_month_weather(self, year_number, month_number):
        # month_url = 'http://lishi.tianqi.com/beijing/201712.html'
        url_list = self.get_url()
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
        
    def get_year_weather(self, year_number):
        year_weather = []
        for i in range(12):
            month_weather = self.get_month_weather(year_number, i+1)
            year_weather.extend(month_weather)
            print '第%d月天气数据采集完成，望您知悉！'%(i+1)
        col_name = ['Date', 'Max_Tem', 'Min_Tem', 'Weather', 'Wind', 'Wind_Level']
        result_df = pd.DataFrame(year_weather)
        result_df.columns = col_name
        # result_df.to_csv('year_weather.csv')
        return result_df

example = get_history_weather()
weather_result = example.get_year_weather(2017)