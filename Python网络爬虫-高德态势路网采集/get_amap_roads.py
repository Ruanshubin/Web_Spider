#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright 2018 Shubin Ruan <ruanshubin.top>
#   All rights reserved.
#   BSD license.
#
#
# Authors: Shubin Ruan <https://github.com/Ruanshubin>
# Created: 2018.08.01
#

"""
通过高德地图交通态势API获取路网

API具体介绍可参照: [https://lbs.amap.com/api/webservice/guide/api/trafficstatus]

"""

import requests
import pandas as pd
import numpy as np
import topology_analysis as rs
import time
import dp2shp
from code_conver import *

def get_url_item(left_bottom, right_top, part_distance):
    """获取URL的params元素，包括'level'和'rectangle'
    
    参数
    ----------
    left_bottom: list[double, double] 区域左下角经纬度坐标
    right_top: list[double, double] 区域右上角经纬度坐标
    part_distance: int 切片的边长 单位为米 高德态势API要求区域的对角线距离不能大于10公里 故该值应小于7000，建议取值为5000 防止漏掉道路信息
    
    返回
    ----------
    url_item_list: list 每个元素也为list 分别为'level'(str)和'rectangle'(str)
    
    """
    
    part_list = rs.grid_cut(left_bottom, right_top, part_distance) # 获取各区域的左下角和右上角坐标
    url_item_list = []
    # 获取'level'和'rectangle'
    for i in range(1, 7):
        # i表征道路的等级信息 取值范围为[1, 6]
        for part in part_list:
            rectangle = str(part[0][0]) + ',' + str(part[0][1]) + ';' + str(part[1][0]) + ',' + str(part[1][1])
            url_item_list.append([str(i), rectangle])
            
    return url_item_list
    
def get_roads(url_item_list, file_name):
    """获取路网数据
    
    参数
    ----------
    url_item_list: list 每个元素也为list 分别为'level'(str)和'rectangle'(str)
    file_name: str shp文件的保存路径
    """
    
    # 基础URL
    base_url = 'https://restapi.amap.com/v3/traffic/status/rectangle'
    # URL属性
    params = {
              'key':'****************************',
              'level':'5',
              'extensions':'all',
              'output':'JSON',
              'rectangle':'116.351147,39.966309;116.357134,39.968727'
              }
    # 将各切片的JSON数据存入result         
    result = []        
    for url_item in url_item_list:
        params['level'] = url_item[0]
        params['rectangle'] = url_item[1]
        response = requests.get(url=base_url, params=params).json()
        result.append([url_item[0], response])
        time.sleep(0.1)
        print '%s等级路网的[%s]区域采集完成' %(url_item[0], url_item[1])
    
    # 提取道路信息
    road_list = []    
    for item in result:
        level = item[0] # 道路等级
        try:
            roads = item[1]['trafficinfo']['roads'] # 区域内道路集合
            if len(roads) > 0:
                for road in roads:
                    road['level'] = level
                    if not (road in road_list):
                        try:
                            polyline = road['polyline']
                            road_list.append(road)
                        except:
                            pass
        except:
            pass
    
    # list to DataFrame 注意将道路的name替换到最前方
    columns = [u'name', u'angle', u'direction', u'lcodes', u'level', u'polyline', u'speed', u'status']                
    roads_df = pd.DataFrame(road_list)
    roads_df = roads_df[columns]
    # 为让ArcGIS正常显示 需要将编码转换为gbk格式
    roads_df = df_code_conver(roads_df, 'gbk')
    
    dp2shp.lines_to_shp(roads_df, file_name)  
    
def test():
    """测试样例  获取昆明市路网数据"""
    
    left_bottom = [102.54358,24.767935]
    right_top = [102.998826,25.138351]
    part_distance = 5000
    
    url_item_list = get_url_item(left_bottom, right_top, part_distance)
    get_roads(url_item_list, 'roads//kunming//roads')
    
    

