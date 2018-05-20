# -*- coding:utf-8 -*-

'采集区域划分'

__author__ = 'RuanShuBin'

import numpy as np

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
    
def poly_max(city_df):
    # 每个城市包含2个元素，第1个为经纬度最大值，第2个为经纬度最小值
    polyline = [[[map(float, point.split(',')) for point in part.split(';')] for part in city.split('|')] for city in list(city_df['polyline'])]
    xy_list = []
    for city in polyline:
        city_xy = []
        for part in city:
            for point in part:
                city_xy.append(point)
        xy_list.append(city_xy)
    xy_max_list = []
    for city in xy_list:
        x_city = [point[0] for point in city]
        y_city = [point[1] for point in city]
        xy_max = map(max, [x_city, y_city])
        xy_min = map(min, [x_city, y_city])
        xy_max_list.append([xy_min, xy_max])
    return xy_max_list
    