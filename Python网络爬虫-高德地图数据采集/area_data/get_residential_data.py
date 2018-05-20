# -*- coding:utf-8 -*-

'获取各居民小区的属性信息'

__author__ = 'RuanShuBin'

import pandas as pd
import numpy as np
from amap_crawler import poi
from amap_crawler import database as db
from amap_crawler import code_conver as cc

params = {
         'query_type':'TQUERY',
         'pagesize':'20',
         'pagenum':'1',
         'qii':'true',
         'cluster_state':'5',
         'need_utd':'true',
         'utd_sceneid':'1000',
         'div':'PC1000',
         'addr_poi_merge':'true',
         'is_classify':'true',
         'zoom':'12',
         'city':'330100',
         'geoobj':'120.087151|30.306204|120.092301|30.3094',
         'keywords':'小区'
         } 

# 城市小区数据保存         
def save_residential(city, keywords, left_bottom, right_top, dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None, part_distance=10000, start_part=0, start_page=0):
	poi.save_all_poi(city, keywords, left_bottom, right_top, dbName, collection, user, port, auth_name, pwd, part_distance, start_part, start_page)
    
def get_residential(dbName, collection, encode='utf-8', user='localhost', port=27017, auth_name=None, pwd=None):
    # residential_df:点df数据
    # residential_area_df:区域df数据
    keys = ['name', 'disp_name', 'id', 'adcode', 'cityname', 'areacode', 'address', 'typecode', 'shape_region', 'longitude', 'latitude']
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    all_page = col.find()
    residential_list = []
    for i in range(all_page.count()):
        page = all_page[i]
        poi_list = page['data']['poi_list']
        for j in range(len(poi_list)):
            poi = poi_list[j]
            temp_list = []
            for key in keys:
                temp_list.append(poi[key])
            try:
                polyline = poi['domain_list'][-1]['value']
                polyline_convent = polyline.replace('_', ';')
            except:
                polyline_convent = 'NaN'           
            temp_list.append(polyline_convent)
            residential_list.append(temp_list)
    keys.append('polyline')
    residential_df = pd.DataFrame(residential_list)
    residential_df.columns = keys
    residential_df.rename(columns={'longitude':'x_coord', 'latitude':'y_coord'}, inplace = True)
    residential_df = residential_df.drop_duplicates()
    residential_area_df = residential_df[residential_df['polyline'] != 'NaN']
    residential_area_df.index = range(residential_area_df.shape[0])
    # 转码
    residential_df = cc.df_code_conver(residential_df, encode)
    residential_area_df = cc.df_code_conver(residential_area_df, encode)
    return residential_df, residential_area_df
    