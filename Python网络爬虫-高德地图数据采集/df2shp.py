# -*- coding:utf-8 -*-

'DataFrame转成shp文件'

__author__ = 'RuanShuBin'

import pandas as pd
import numpy as np
import shapefile 

'''
转成shp文件时:
    columns为'utf-8'或'gbk'格式
    values必须为gbk格式，否则会报错。        
'''

# 点shp文件生成
# 'x_coord', 'y_coord'分别为点的横纵坐标
def points_to_shp(points_df, file_name):
    keys = list(points_df.columns)
    w = shapefile.Writer(shapefile.POINT)
    for key in keys:
        w.field(key)
    points_num = points_df.shape[0]
    for i in range(points_num):
        point = points_df.iloc[i]
        if type(point['x_coord']) == np.float64:
            w.point(point['x_coord'], point['y_coord'])
        elif type(point['x_coord']) == str or type(point['x_coord']) == unicode:
            w.point(float(point['x_coord']), float(point['y_coord']))
        point_list = list(point)
        w.record(*point_list)
        print '第%d个点生成shp文件成功，一共%d个点！'%(i+1, points_num)
    w.save(file_name)

# 线shp文件生成  
# 'xs', 'ys'为线的横纵坐标集合，字符串类型
def lines_to_shp(lines_df, file_name):
    w = shapefile.Writer(shapefile.POLYLINE)
    xs_list = [map(float, example) for example in [example.split(',') for example in list(lines_df['xs'])]]
    ys_list = [map(float, example) for example in [example.split(',') for example in list(lines_df['ys'])]]
    # del lines_df['xs']
    # del lines_df['ys']
    keys = list(lines_df.columns)
    for key in keys:
        w.field(key)
    lines_num = lines_df.shape[0]
    for i in range(lines_num):
        line_xs, line_ys = xs_list[i], ys_list[i]
        parts = [[line_xs[j], line_ys[j]] for j in range(len(line_xs))]
        w.line(parts=[parts]) # 此处使用line，而不用poly，poly会在最后添加起点，以使线段闭合
        # 注意parts需要加上中括号，否则会报错
        line = lines_df.iloc[i]
        line_list = list(line)
        w.record(*line_list)
        print '第%d个线路生成shp文件成功，一共%d个线路！'%(i+1, lines_num)
    w.save(file_name)

# 面shp文件生成
'''
'polyline'为区域的边界坐标
同一区域的不同区块以'|'分割
相同区块边界点以';'分割
点的经、纬度以','分割   
'''
def polygon_to_shp(polygon_df, file_name):
    w = shapefile.Writer(shapefile.POLYGON)
    keys = list(polygon_df.columns)
    for key in keys:
        w.field(key)
    polygon_num = polygon_df.shape[0]
    for i in range(polygon_num):
        polyline = polygon_df['polyline'][i]
        polyline_list = [[map(float, point.split(',')) for point in poly.split(';')] for poly in polyline.split('|')]
        w.poly(parts=polyline_list) # 多个线时，无需加[]
        record_list = list(polygon_df.iloc[i])
        # record_list = [example.encode('gbk') if type(example)!=float else example for example in record_list]
        w.record(*record_list)
        print '第%d个区域生成shp文件成功，一共%d个区域！'%(i+1, polygon_num)
    w.save(file_name)
    