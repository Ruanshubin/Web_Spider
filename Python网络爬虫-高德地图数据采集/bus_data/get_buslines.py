# -*- coding:utf-8 -*-

'公交线路数据获取'

__author__ = 'RuanShuBin'

import pandas as pd
import numpy as np
from amap_crawler import database as db 
from amap_crawler import code_conver as cc

def get_buslines(dbName, collection, encode='utf-8', user='localhost', port=27017, auth_name=None, pwd=None):
    # user = 'localhost'; port = 27017; dbName = 'bus_data'; collection = 'lines'
    col = db.MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    lines_list = col.find()  
    keys = list(lines_list[0]['data']['busline_list'][0].keys())
    keys.remove('stations')
    buslines = []
    for lines in lines_list:
        if lines['data']['busline_count'] != 0:
            busline_list = lines['data']['busline_list']
            for busline in busline_list:
                del busline['stations']
                buslines.append(busline)
    buslines_df = pd.DataFrame(buslines)
    keys_new = ['key_name', 'name']
    for key in keys_new:
        keys.remove(key)
    keys_new.extend(keys)
    buslines_df = buslines_df[keys_new]
    buslines_df.columns = keys_new
    # 编码转换
    buslines_df = cc.df_code_conver(buslines_df, encode)
    return buslines_df