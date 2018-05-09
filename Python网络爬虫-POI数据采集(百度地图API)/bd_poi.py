# -*- coding:utf-8 -*-

'POI数据获取'

__author__ = 'RuanShuBin'

import requests
import pandas as pd
import numpy as np
from pymongo import MongoClient
import time

# 计算两点间直线距离
def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）  
    """ 
    Calculate the great circle distance between two points  
    on the earth (specified in decimal degrees) 
    """  
    # 将十进制度数转化为弧度  
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])  
    # haversine公式  
    dlon = lon2 - lon1   
    dlat = lat2 - lat1   
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2  
    c = 2 * np.arcsin(np.sqrt(a))   
    EARTH_REDIUS = 6378.137 # 地球平均半径，单位为公里  
    distance = c * EARTH_REDIUS * 1000  
    return distance

# 区域切片
def grid_cut(left_bottom, right_top, part_distance=10000): 
    # left_bottom:左下角坐标 right_top：右上角坐标
    # part_distance:切片的边长
    x_dis = haversine(left_bottom[0], left_bottom[1], right_top[0], left_bottom[1]) # 横向距离
    y_dis = haversine(left_bottom[0], left_bottom[1], left_bottom[0], right_top[1]) # 纵向距离
    x_n = int(np.ceil(x_dis/part_distance)) # 横向切片个数
    y_n = int(np.ceil(y_dis/part_distance)) # 纵向切片个数
    x_range = right_top[0] - left_bottom[0] # 横向经度差
    y_range = right_top[1] - left_bottom[1] # 纵向纬度差
    part_x = x_range/x_n # 切片横向距离
    part_y = y_range/y_n # 切片纵向距离
    part_list = []
    for i in range(x_n):
        for j in range(y_n):
            part_left_bottom = [left_bottom[0]+i*part_x, left_bottom[1]+j*part_y]
            part_right_top = [right_top[0]+i*part_x, right_top[1]+j*part_y]
            part_list.append([part_left_bottom, part_right_top])
    return part_list

'mongo数据库'
# cmd启动服务
# mongod --dbpath=D:\MongoDB\data\db
# 另开cmd，mongo
# use bus_data
'''
db.createUser({
    "user":"hello",
    "pwd":"python",
    "roles":[{"role":"readWrite","db":"bank_data"}]
}   
)
'''

def MongoDB_login(dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None):
    '''
    user:用户名
    port:端口号
    dbName:数据库名
    collection:表名
    '''
    client = MongoClient(user, port)
    db = client[dbName]
    if auth_name:
        db.authenticate(auth_name, pwd)
    col = db[collection]; # 连接集合
    return col
    
'城市POI数据采集'

# 切片数据采集
def get_part_poi(part_left_bottom, part_right_top, query, ak, dbName, collection, part_total=1, part_num=1, page_size='20', user='localhost', port=27017, auth_name=None, pwd=None):
    poi_url = 'http://api.map.baidu.com/place/v2/search?'
    # 参数配置
    bounds = str(part_left_bottom[1]) + ',' + str(part_left_bottom[0])
    bounds += ',' + str(part_right_top[1]) + ',' + str(part_right_top[0])
    params = {
            'query':query,
            'bounds':bounds,
            'output':'json',
            'scope':'2',
            'coord_type':'1',
            'page_size':page_size,
            'page_num':'19',
            'ak':ak
            }
    response = requests.get(poi_url, params=params).json()
    poi_total = response['total'] # 区域POI个数
    page_total = poi_total/int(page_size) # 总页数
    # 登录MongoDB数据库
    col = MongoDB_login(dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None)
    for i in range(page_total):
        params['page_num'] = str(i)
        response = requests.get(poi_url, params=params).json()
        if response['message'] == u'ok':
            for poi in response['results']:
                col.insert_one(poi)
        print '第%d个切片的第%d页数据采集完成，望您知悉！'%(part_num, i+1)
        time.sleep(1)

# 全部数据采集        
def get_all_poi(query, ak, dbName, collection, left_bottom, right_top, part_distance=10000, page_size='20', user='localhost', port=27017, auth_name=None, pwd=None):
    part_list = grid_cut(left_bottom, right_top, part_distance)
    part_total = len(part_list)
    for i in range(len(part_list)):
        part = part_list[i]
        part_num = i+1
        get_part_poi(part[0], part[1], query, ak, dbName, collection, part_total, part_num, page_size, user, port, auth_name, pwd)
        
# 要素编码转化
def item_code_conver(item, to_code):
    if type(item) == str:
        try:
            item = item.decode('utf-8')
        except:
            item = item.decode('gbk')
    if to_code != 'unicode':
        if type(item) == unicode:
            try:
                item = item.encode(to_code)
            except:
                item = item.encode('utf-8')
    return item
    
# from_code: 'unicode' 'utf-8' 'gbk'
# DataFrame编码转化
def df_code_conver(initial_df, to_code, key_code='utf-8'):
    keys = list(initial_df.columns)
    for key in keys:
        key_list = list(initial_df[key])
        key_list_new = map(item_code_conver, key_list, [to_code]*len(key_list))
        initial_df[key] = key_list_new
    # keys统一转化成utf-8编码
    keys_new = map(item_code_conver, keys, [key_code]*len(keys))
    initial_df.columns = keys_new   
    return initial_df
        
# 数据解析并存储为csv文件
def save_csv(dbName, collection, file_name, user='localhost', port=27017, auth_name=None, pwd=None):
    col = MongoDB_login(dbName, collection, user, port, auth_name, pwd)
    results = list(col.find())
    results_df = pd.DataFrame(results)
    results_df = df_code_conver(results_df, 'utf-8')
    results_df.to_csv(file_name)

'''程序测试'''

# 参数设置    
query = '酒店'
ak = '***************' # 百度API的ak
dbName = 'POI_guiyang' # 数据库名
collection = 'hotel' # 表名 
left_bottom = [106.517784,26.356445] # 城市左下角坐标
right_top = [106.806175,26.713975] # 城市右上角坐标
file_name = 'D:\poi_data\hotel.csv'
# 获取城市所有POI并存储进MongoDB
get_all_poi(query, ak, dbName, collection, left_bottom, right_top, part_distance=5000)
# 保存为csv文件
save_csv(dbName, collection, file_name)
