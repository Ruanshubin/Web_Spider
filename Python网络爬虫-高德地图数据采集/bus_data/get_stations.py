# -*- coding:utf-8 -*-

'公交站点数据获取'

__author__ = 'RuanShuBin'

import pandas as pd
import numpy as np
from amap_crawler import database as db 
from amap_crawler import code_conver as cc
			
# 获取公交站点数据
# dbName = 'bus_data'; collection = 'lines'
def get_stations(dbName, collection, encode='utf-8', user='localhost', port=27017, auth_name=None, pwd=None):
    keys = ['name','line_name','company','poiid1','poiid2','start_time','end_time','spell','status','trans_flag','code','station_id','station_num']
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    lines_list = col.find()
    stations_list = []
    for i in range(lines_list.count()):
        if lines_list[i]['data']['busline_count'] != 0:
            busline_list = lines_list[i]['data']['busline_list']
            for j in range(len(busline_list)):
                line_name = busline_list[j]['name']
                company = busline_list[j]['company']
                line_stations = busline_list[j]['stations']
                for k in range(len(line_stations)):
                    station = line_stations[k]
                    station['line_name'] = line_name
                    station['company'] = company
                    station_list = []
                    for key in keys:
                        station_list.append(station[key])
                    station_list.extend(map(float, station['xy_coords'].split(';')))
                    stations_list.append(station_list)
        print '%d条线路转换完成！'%(i+1)
    keys.extend(['x_coord', 'y_coord'])
    stations_df = pd.DataFrame(stations_list)
    stations_df.columns = keys
    stations_df = cc.df_code_conver(stations_df, encode)
    return stations_df
    
# 获取公交站点聚类数据
def get_stations_cluster(dbName, collection, encode='utf-8', user='localhost', port=27017, auth_name=None, pwd=None):
    stations_df = get_stations(dbName, collection, encode, user, port, auth_name, pwd)
    keys = ['name', 'poiid1', 'poiid2', 'spell', 'x_coord', 'y_coord']
    stations_df_new = stations_df[keys]
    xy_means = stations_df_new.groupby('poiid1').mean()
    xy_means['poiid1'] = list(xy_means.index)
    del stations_df_new['x_coord']
    del stations_df_new['y_coord']
    stations_cluster_df = pd.merge(xy_means, stations_df_new).drop_duplicates() 
    stations_cluster_df = stations_cluster_df[keys]
    stations_cluster_df.index = range(stations_cluster_df.shape[0])
    stations_cluster_df = cc.df_code_conver(stations_cluster_df, encode)
    return stations_cluster_df