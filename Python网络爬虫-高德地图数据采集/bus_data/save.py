# -*- coding:utf-8 -*-

'公交数据保存'

__author__ = 'RuanShuBin'

import requests
from amap_crawler import poi
from amap_crawler import database as db

keywords = '公交站'

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
         'keywords':keywords
         } 

# 公交站点数据获取，主要是为了提取各站点包含的线路名称，然后去重得到城市内的全部线路名称		 
def save_stations(city, left_bottom, right_top, dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None, part_distance=10000, start_part=0, start_page=0):
	poi.save_all_poi(city, keywords, left_bottom, right_top, dbName, collection, user, port, auth_name, pwd, part_distance, start_part, start_page)

# 获取全部公交线路名称
def get_busline_names(dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None):
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    line_list = col.find()
    name_list = []
    for i in range(line_list.count()):
        line = line_list[i]['data']['poi_list']
        for j in range(len(line)):
            name_list.extend(line[j]['address'].split(';'))
    name_list = list(set(name_list))        
    name_list.sort()
    return name_list
    
# 公交线路数据存储
def save_buslines(city, name_list, left_bottom, right_top, dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None, start_num=0):
    geoobj = str(left_bottom[0]) + '|' + str(left_bottom[1]) + '|' + str(right_top[0]) + '|' + str(right_top[1])
    params['city'] = city
    params['geoobj'] = geoobj
    params['pagenum'] = '1'
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    for i in range(start_num, len(name_list)):
        line_name = name_list[i].encode('utf-8')
        line_name = line_name.replace('(停运)', '')
        params['keywords'] = line_name
        line_url = 'https://www.amap.com/service/poiInfo?'
        response = requests.get(url=line_url, params=params).json()
        if response[u'status'] == u'1':
            col.insert_one(response)
            print '第%d条线路%s数据采集完成，该线路包含%d条数据，一共%d条线路！'%(i, line_name, int(response['data']['busline_count']), len(name_list)-1)
        else:
            break