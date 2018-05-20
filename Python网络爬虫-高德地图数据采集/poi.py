# -*- coding:utf-8 -*-

'POI数据获取'

__author__ = 'RuanShuBin'

import requests
import pandas as pd
import numpy as np
from . import topology_analysis as rs
from . import database as db 

poi_url = 'https://www.amap.com/service/poiInfo?'

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
         'keywords':'银行'
         }    

# 切片POI点获取
def get_part_poi(city, geoobj, keywords, dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None, part_num=0, start_page=0, part_total=0):
    params['city'] = city
    params['geoobj'] = geoobj
    params['keywords'] = keywords
    response = requests.get(url=poi_url, params=params).json()
    total = int(response['data']['total']) # 个数
    pagenum = int(np.ceil(total/20.0))
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    for i in range(start_page, pagenum):
        params['pagenum'] = str(i+1)
        response = requests.get(url=poi_url, params=params).json()
        if response[u'status'] == u'1':
            poi_list = response['data']['poi_list']
            name = poi_list[0]['name']
            disp_name = poi_list[0]['disp_name']
            if name == disp_name:
                col.insert_one(response)
                print '第%d个切片的第%d页数据入库完成,一共%d个切片！'%(part_num, i, part_total-1)
            else:
                print '程序运行错误，重新进行地图验证！'
                i -= 1
                break
    return i+1, pagenum
    
# 保存全部POI点
def save_all_poi(city, keywords, left_bottom, right_top, dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None, part_distance=10000, start_part=0, start_page=0):
    part_list = rs.grid_cut(left_bottom, right_top, part_distance)
    part_total = len(part_list)
    for i in range(start_part, part_total):
        geoobj = str(part_list[i][0][0]) + '|' + str(part_list[i][0][1]) + '|' + str(part_list[i][1][0]) + '|' + str(part_list[i][1][1])
        part_end_num, pagenum = get_part_poi(city, geoobj, keywords, dbName, collection, user, port, auth_name, pwd, part_num=i, start_page=start_page, part_total=part_total)
        if part_end_num == pagenum:
            start_page = 0
        else:
            break