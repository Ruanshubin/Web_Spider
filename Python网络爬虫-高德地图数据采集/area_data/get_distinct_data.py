# -*- coding:utf-8 -*-

'获取各行政区划的属性信息'

__author__ = 'RuanShuBin'

import requests
import pandas as pd
import numpy as np
from amap_crawler import database as db
from amap_crawler import code_conver as cc

request_url = 'https://restapi.amap.com/v3/config/district?'
params = {
         'subdistrict':'3',
         'showbiz':'false',
         'extensions':'all',
         'key':'160cab8ad6c50752175d76e61ef92c50',
         's':'rsv3',
         'output':'json',
         'keywords':'中国',
         }

def get_distinct_attribute(level, encode='utf-8'):         
    response = requests.get(url=request_url, params=params).json()
    # 国
    country = response['districts']
    keys_country = ['name', 'level', 'adcode', 'center']
    country_df = pd.DataFrame(country)
    country_df = country_df[keys_country]
    country_df = cc.df_code_conver(country_df, encode)
    # 省
    country = response['districts']
    provinces = []
    country_name = country[0]['name']
    for province in country[0]['districts']:
        province['country'] = country_name
        provinces.append(province)
    provinces_df = pd.DataFrame(provinces)
    keys_province = ['name', 'level', 'adcode', 'center', 'country']
    provinces_df = provinces_df[keys_province]
    provinces_df = cc.df_code_conver(provinces_df, encode)
    # 市
    cities = []
    for province in provinces:
        country_name = province['country']
        province_name = province['name']
        for city in province['districts']:
            city['country'] = country_name
            city['province'] = province_name
            cities.append(city)
    cities_df = pd.DataFrame(cities)
    cities_df_true = cities_df[cities_df['level']=='city']
    keys_city = ['name', 'level', 'adcode', 'center', 'country', 'province']
    cities_df_true = cities_df_true[keys_city]
    cities_df_true.index = range(cities_df_true.shape[0])
    cities_df_true = cc.df_code_conver(cities_df_true, encode)
    # 区
    districts = []
    for city in cities:
        country_name = city['country']
        province_name = city['province']
        city_name = city['name']
        for district in city['districts']:
            district['country'] = country_name
            district['province'] = province_name
            district['city'] = city_name
            districts.append(district)
    districts_df = pd.DataFrame(districts)
    districts_df_true = pd.concat([cities_df[cities_df['level']=='district'], districts_df[districts_df['level']=='district']])
    districts_df_true.index = range(districts_df_true.shape[0])
    keys_district = ['name', 'level', 'adcode', 'center', 'country', 'province', 'city']
    districts_df_true = districts_df_true[keys_district]
    districts_df_true = cc.df_code_conver(districts_df_true, encode)
    # 各属性集合
    distinct_list = [country_df, provinces_df, cities_df_true, districts_df_true]
    # 判断语句
    if level == 'all':
        return distinct_list
    else:
        return distinct_list[level]
        
def save_polygon(polygon_df, dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None, start_num=0):
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    request_url = 'https://restapi.amap.com/v3/config/district?'
    params['subdistrict'] = '0'
    polygon_num = polygon_df.shape[0]
    for i in range(start_num, polygon_num):
        keywords = polygon_df['adcode'][i]
        params['keywords'] = keywords
        response = requests.get(url=request_url, params=params).json()
        col.insert_one(response)
        print '第%d个区域入库成功，一共%d个区域！'%(i, polygon_num-1)
 
# 添加'polyline' 
def get_polygon_df(polygon_df, dbName, collection, encode='utf-8', user='localhost', port=27017, auth_name=None, pwd=None):
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    response_list = col.find()
    polygon_df['polyline'] = 'NaN'
    polygon_num = response_list.count()
    for i in range(polygon_num):
        response = response_list[i]
        polyline = response['districts'][0]['polyline']
        polygon_df['polyline'][i] = polyline
        print '第%d个区域数据获取成功，一共%d个区域！'%(i, polygon_num-1)
    polygon_df = cc.df_code_conver(polygon_df, encode)
    return polygon_df        
        