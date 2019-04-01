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
通过地图API实现坐标系的转换

支持：
    百度地图
    高德地图
    
转换之前为'longitude' 'latitude'
转换之后为'x' 'y'

add_polyline: 横、纵坐标为'x' 'y'
"""

import numpy as np
import pandas as pd
import requests
import time
from code_conver import *
import shapefile 



def get_coords_list(coords_df, coords_num=100, split_str=';'):
    """将100个点的经纬度拼接成coords
    
    参数
    ----------
    coords_df: DataFrame 点的DataFrame数据 其中包含'longitude'和'latitude'列 且数据格式为str
    coords_num: int API支持的一次访问量
    split_str: str 坐标对之间的分割符
    
    返回
    ----------
    params_list: list 元素为coords字符串
    
    """
    params_list = [] # 生成待处理的params集合 主要是coords字符串的拼接，因为其单次请求可批量解析多个坐标
    for i in range(coords_num, coords_df.shape[0]+1, coords_num):
        temp = coords_df.iloc[i-coords_num:i]
        coords = ''
        for j in range(temp.shape[0]):
            coords = coords + temp['longitude'][i+j-coords_num] + ',' + temp['latitude'][i+j-coords_num] + split_str # 在pandas下，切分数据index不会变，所以要注意
        coords = coords.strip(split_str) # 去除末尾多的一个';'
        params_list.append(coords)
    n = coords_df.shape[0]
    if n%coords_num != 0:
        temp = coords_df.iloc[n/coords_num*coords_num:n]
        coords = ''
        for i in temp.index:
            coords = coords + temp['longitude'][i] + ',' + temp['latitude'][i] + split_str
        coords = coords.strip(split_str)
        params_list.append(coords)
    return params_list

def baidu_coord_trans(coords_df, coord_from, coord_to, ak):
    """基于百度地图API进行坐标转换
    
    参数
    ----------
    coords_df: DataFrame 点的DataFrame数据 其中包含'longitude'和'latitude'列 且数据格式为str
    coord_from: str 源坐标类型
        1：GPS设备获取的角度坐标，wgs84坐标;
        2：GPS获取的米制坐标、sogou地图所用坐标;
        3：google地图、soso地图、aliyun地图、mapabc地图和amap地图所用坐标，国测局（gcj02）坐标;
        4：3中列表地图坐标对应的米制坐标;
        5：百度地图采用的经纬度坐标;
        6：百度地图采用的米制坐标;
        7：mapbar地图坐标;
        8：51地图坐标
    coord_to: str 目标坐标类型
        3：国测局（gcj02）坐标;
        4：3中对应的米制坐标;
        5：bd09ll(百度经纬度坐标);
        6：bd09mc(百度米制经纬度坐标)
    ak: str 开发者密钥,用户申请注册的key
    
    返回
    ----------
    result_df: DataFrame 坐标转换之后的结果
    
    """
    
    # 基础URL
    base_url = 'http://api.map.baidu.com/geoconv/v1/'
    # URL属性
    params = {
              'coords':'114.21892734521,29.575429778924',
              'ak':'***************************',
              'from':'1',
              'to':'5',
              'output':'json'
              } 
    params_list = get_coords_list(coords_df)
    result_list = []
    params['from'] = coord_from
    params['to'] = coord_to
    params['ak'] = ak
    for i in range(len(params_list)):
        params['coords'] = params_list[i]
        response = requests.get(url=base_url, params=params).json()
        if response['status'] == 0:
            temp = []
            for point in response['result']:
                temp.append([point['x'],point['y']])
            result_list.extend(temp)
        else:
            print '第%d次调用失败, x,y均已1代替!' %(i+1)
            temp = []
            if i < len(params_list)-1:
                for j in range(100):
                    temp.append([1,1])
                result_list.extend(temp)
            else:
                for j in range(coords_df.shape[0]-i*100):
                    temp.append([1,1])
                result_list.extend(temp)
        
        time.sleep(0.01) # 1分钟只能发送6000次
    coords_df['x'] = [example[0] for example in result_list]
    coords_df['y'] = [example[1] for example in result_list]
    return coords_df
    

def amap_coord_trans(coords_df, coord_from, ak):
    """基于高德地图API进行坐标转换

    摘要
    ---------
    坐标转换是一类简单的HTTP接口，能够将用户输入的非高德坐标（GPS坐标、mapbar坐标、baidu坐标）转换成高德坐标。
    
    经度和纬度用","分割，经度在前，纬度在后，经纬度小数点后不得超过6位。多个坐标对之间用”|”进行分隔最多支持40对坐标。
    
    参数
    ----------
    coords_df: DataFrame 点的DataFrame数据 其中包含'longitude'和'latitude'列 且数据格式为str
    coord_from: str 源坐标类型
                    gps;
                    mapbar;
                    baidu;
                    autonavi(不进行转换)
    ak: str 用户在高德地图官网申请Web服务API类型KEY
    
    返回
    ----------
    result_df: DataFrame 坐标转换之后的结果
    
    """
    
    # 基础URL
    base_url = 'https://restapi.amap.com/v3/assistant/coordinate/convert'
    # URL属性
    params = {
              'locations':'114.21892734521,29.575429778924',
              'key':'*****************************',
              'coordsys':'gps',
              'output':'JSON'
              } 
    params_list = get_coords_list(coords_df, coords_num=40, split_str='|')
    result_list = []
    params['coordsys'] = coord_from
    params['key'] = ak
    for i in range(len(params_list)):
        params['locations'] = params_list[i]
        response = requests.get(url=base_url, params=params).json()
        if response['status'] == '1':
            temp = []
            points = response['locations'].split(';')
            for point in points:
                temp.append(point.split(','))
            result_list.extend(temp)
            print '第%d次调用成功!' %(i+1)
        else:
            print '第%d次调用失败, x,y均已1代替!' %(i+1)
            temp = []
            if i < len(params_list)-1:
                for j in range(40):
                    temp.append([1,1])
                result_list.extend(temp)
            else:
                for j in range(coords_df.shape[0]-i*40):
                    temp.append([1,1])
                result_list.extend(temp)
        
        time.sleep(0.01) # 1分钟只能发送6000次
    coords_df['x'] = [example[0] for example in result_list]
    coords_df['y'] = [example[1] for example in result_list]
    return coords_df

def get_shp_coords(file_name):
    """获取线shp文件的内点坐标
    
    参数
    ----------
    file_name: str shp文件的路径
    
    返回
    ----------
    coords_df: DataFrame 包含3列 'point_index'为线的编号(int 0开始) 'longitude', 'latitude'为经纬度
    """
    shape_obj = shapefile.Reader(file_name)
    # 获取点的坐标
    shapes = shape_obj.shapes()
    lines_point = []
    for line in shapes:
        lines_point.append([len(line.points),line.points])
    coords_list = []
    point_index = [] # 点的编号 标注归属哪个线
    temp = 0
    for points in lines_point:
        coords_list.extend(points[1])
        point_index.extend([temp] * points[0])
        temp += 1
    
    # 将数字保留小数点后6位(高德要求) 转为字符串
    coords_list = [map(lambda x: '%.6f' % x, example) for example in coords_list]
    coords_df = pd.DataFrame(coords_list)
    coords_df.columns = ['longitude', 'latitude']
    coords_df['point_index'] = point_index
    return coords_df
    
    
    
def add_polyline(file_name, coords_df):
    """在路网数据的DataFrame中添加'polyline'
    
    参数
    ----------
    file_name: str shp文件的路径
    coords_df: DataFrame 至少包含3列 'point_index'为线的编号(int 0开始) 'x', 'y'为经纬度
    
    返回
    -----------
    lines_df: DataFrame 线的DataFrame 可基于lines_to_shp函数生成shp文件
    
    """
    shape_obj = shapefile.Reader(file_name)
    # 记录
    lines_list = list(shape_obj.records())
    # 列名
    line_fields = shape_obj.fields
    columns = [example[0] for example in line_fields]
    del columns[0] # 第一项为fields标签，删除
    lines_df = pd.DataFrame(lines_list, columns = columns)
    # 将相同线路的坐标点合成1个字符串
    polyline_list = []
    for i in range(lines_df.shape[0]):
        temp = coords_df[coords_df['point_index'] == i]
        temp.index = range(temp.shape[0])
        polyline = ''
        for j in range(temp.shape[0]):
            polyline =  polyline + temp['x'][j] + ',' + temp['y'][j] + ';'
        polyline_list.append(polyline.strip(';'))
    lines_df['polyline'] = polyline_list
    return lines_df
    

def wgs84_bd(coords_df, ak):
    """基于百度地图API进行坐标转换 wgs84_bd

    摘要
    ---------
    此函数是以wgs84_bd为基础的
    假设你有百度坐标：x1=116.397428，y1=39.90923 
    把这个坐标当成GPS坐标，通过接口获得他的百度坐标：x2=116.41004950566，y2=39.916979519873
    通过计算就可以得到GPS的坐标： 
    x = 2*x1-x2，y = 2*y1-y2 
    
    参数
    ----------
    coords_df: DataFrame 点的DataFrame数据 其中包含'longitude'和'latitude'列 且数据格式为str
    ak: str 开发者密钥,用户申请注册的key
    
    返回
    ----------
    result_df: DataFrame 坐标转换之后的结果
    
    """  
    coords_df = baidu_coord_trans(coords_df, '1', '5', ak)
    coords_df['x_gps'] = map(lambda x, y: 2 * float(x) - y, list(coords_df['longitude']), list(coords_df['x']))
    coords_df['y_gps'] = map(lambda x, y: 2 * float(x) - y, list(coords_df['latitude']), list(coords_df['y']))
    
    return coords_df
    
def test():
    """测试函数 将乌鲁木齐OSM路网(WGS84 坐标)转为火星坐标"""
    
    file_name = 'data//wulumuqi//edges//edges.shp'
    # 获取路网的内点数据
    coords_df = get_shp_coords(file_name)
    # 坐标转换
    coords_df = amap_coord_trans(coords_df, 'gps', 'a3fb0c430042c7bd7cd1353a2f0f1992')
    # 添加'polyline'
    lines_df = add_polyline(file_name, coords_df)
    # 将DataFrame编码改为gbk 以支持ArcMap
    lines_df = df_code_conver(lines_df, 'gbk')
    # 生成shp文件
    lines_to_shp(lines_df, 'amap//hangzhou//edges')
    return True
        