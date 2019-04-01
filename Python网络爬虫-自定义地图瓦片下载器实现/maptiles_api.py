#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright 2018 Shubin Ruan <ruanshubin.top>
#   All rights reserved.
#   BSD license.
#
#
# Authors: Shubin Ruan <https://github.com/Ruanshubin>
# Created: 2018.07.05
#


"""
地图瓦片处理的接口
"""
    
import math
import numpy as np
import pandas as pd
import os


"""
百度及高德地图参数配置
"""

"""百度地图配置 'normal' 普通地图 'custom':定制地图 'satellite':卫星图"""

baidu = {
         'base_url':{
                     'normal': 'http://online0.map.bdimg.com/onlinelabel/',
                     'custom': 'http://api0.map.bdimg.com/customimage/tile',
                     'satellite': 'https://ss0.bdstatic.com/8bo_dTSlR1gBo1vgoIiO_jowehsv/starpic/'
                     },
         'pre_num':{
                     'normal': 'online',
                     'custom': 'api',
                     'satellite': 'ss'
                    },
         'server_begin':{
                     'normal': '0',
                     'custom': '0',
                     'satellite': '0'
                    },
         'params':{
                     'normal': {
                                'qt':'tile',
                                'x':'0',
                                'y':'0',
                                'z':'0',
                                'styles':'pl',
                                'udt':'20160321',
                                'scaler':'2',
                                'p':'1'
                                },
                     'custom': {
                                'x':'0',
                                'y':'0',
                                'z':'0',
                                'udt':'20180601',
                                'scale':'1',
                                'styles':'t:water|e:all|c:#031628,t:land|e:g|c:#000102,t:highway|e:all|v:off,t:arterial|e:g.f|c:#000000,t:arterial|e:g.s|c:#0b3d51,t:local|e:g|c:#000000,t:railway|e:g.f|c:#000000,t:railway|e:g.s|c:#08304b,t:subway|e:g|l:-70,t:building|e:g.f|c:#000000,t:all|e:l.t.f|c:#857f7f,t:all|e:l.t.s|c:#000000,t:building|e:g|c:#022338,t:green|e:g|c:#062032,t:boundary|e:all|c:#465b6c,t:manmade|e:all|c:#022338,t:label|e:all|v:off'
                                },
                     'satellite': {
                                'qt':'satepc',
                                'u':'x=0;y=0;z=0;v=009;type=sate',
                                'fm':'46',
                                'app':'webearth2',
                                'v':'009',
                                'udt':'20180614',
                                }
                   },
         'server_num':{
                     'normal': '4',
                     'custom': '3',
                     'satellite': '4'
                     }
         }
 

"""
高德地图配置

摘要
----------
http://webst0{1-4}.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}

通过zh_cn设置中文，en设置英文，size基本无作用，scl设置标注还是底图，scl=1代表注记，scl=2代表底图（矢量或者影像），style设置影像和路网，style=6为影像图，style=7为矢量路网，style=8为影像路网
"""
amap = {
        'base_url':'http://webst01.is.autonavi.com/appmaptile',
        'server_begin':'01',
        'params': {
                    'lang':'zh_cn',
                    'size':'1',
                    'scale':'1',
                    'style':'7',
                    'x':'0',
                    'y':'0',
                    'z':'0'
                },
        'server_num': '4'
        }
        
map_setting = {'baidu':baidu, 'amap':amap}

TILE_PIXEL_UNIT = 256.0 # 切片大小
EARTH_RADIUS = 6370996.81 # 地球半径
MCBAND = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
LLBAND = [75, 60, 45, 30, 15, 0]
MC2LL = [[1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331,
          200.9824383106796, -187.2403703815547, 91.6087516669843,
          -23.38765649603339, 2.57121317296198, -0.03801003308653, 17337981.2],
         [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289,
          96.32687599759846, -1.85204757529826, -59.36935905485877,
          47.40033549296737, -16.50741931063887, 2.28786674699375, 10260144.86],
         [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616,
          59.74293618442277, 7.357984074871, -25.38371002664745,
          13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
         [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591,
          40.31678527705744, 0.65659298677277, -4.44255534477492,
          0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
         [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062,
          23.10934304144901, -0.00023663490511, -0.6321817810242,
          -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
         [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8,
          7.47137025468032, -0.00000353937994, -0.02145144861037,
          -0.00001234426596, 0.00010322952773, -0.00000323890364, 826088.5]
         ]
LL2MC = [[-0.0015702102444, 111320.7020616939, 1704480524535203,
          -10338987376042340, 26112667856603880, -35149669176653700,
          26595700718403920, -10725012454188240, 1800819912950474, 82.5],
         [0.0008277824516172526, 111320.7020463578, 647795574.6671607,
          -4082003173.641316, 10774905663.51142, -15171875531.51559,
          12053065338.62167, -5124939663.577472, 913311935.9512032, 67.5],
         [0.00337398766765, 111320.7020202162, 4481351.045890365,
          -23393751.19931662, 79682215.47186455, -115964993.2797253,
          97236711.15602145, -43661946.33752821, 8477230.501135234, 52.5],
         [0.00220636496208, 111320.7020209128, 51751.86112841131,
          3796837.749470245, 992013.7397791013, -1221952.21711287,
          1340652.697009075, -620943.6990984312, 144416.9293806241, 37.5],
         [-0.0003441963504368392, 111320.7020576856, 278.2353980772752,
          2485758.690035394, 6070.750963243378, 54821.18345352118,
          9540.606633304236, -2710.55326746645, 1405.483844121726, 22.5],
         [-0.0003218135878613132, 111320.7020701615, 0.00369383431289,
          823725.6402795718, 0.46104986909093, 2351.343141331292,
          1.58060784298199, 8.77738589078284, 0.37238884252424, 7.45]]


def ll2mercator_bd(lng, lat): # 地理坐标->墨卡托坐标
    """将百度坐标转换为墨卡托坐标
    
    参数
    ----------
    lng: number 经度
    lat: number 纬度
    
    返回
    ----------
    x: number 墨卡托横坐标
    y: number 墨卡托纵坐标
    """
    ll2mc = None
 
    # JavaScript API处理前对经纬度的范围进行了框定
    # T.lng = this.getLoop(T.lng, -180, 180);
    # T.lat = this.getRange(T.lat, -74, 74);
   
    for i in xrange(0, len(LLBAND)):
        if lat >= LLBAND[i]:
            ll2mc = LL2MC[i]
            break

    if not ll2mc:
        for i in xrange(0, len(LLBAND)).reverse():
            if lat <= -LLBAND[i]:
                ll2mc = LL2MC[i]
                break

    x, y = convertor_bd(lng, lat, ll2mc)

    return x, y
    
def convertor_bd(lng, lat, param_list):  
    """百度地理坐标及墨卡托互转需要用到的函数
    
    参数
    ----------
    lng: number 经度
    lat: number 纬度
    param_list: list 参数
    
    返回
    ----------
    x: number 墨卡托横坐标
    y: number 墨卡托纵坐标
    """
    x = param_list[0] + param_list[1]*abs(lng)
    a = abs(lat)/param_list[9]
    y = param_list[2] + param_list[3]*a + param_list[4]*pow(a, 2) + param_list[5]*pow(a, 3)
    y += param_list[6]*pow(a, 4) + param_list[7]*pow(a, 5) + param_list[8]*pow(a, 6)

    x *= (1 if lng > 0 else -1)
    y *= (1 if lat > 0 else -1)
    
    del param_list
    del a
    
    return x, y
    
def mercator2ll_bd(x, y): 
    """墨卡托坐标->百度地理坐标
    
    参数
    ----------
    x: number 墨卡托横坐标
    y: number 墨卡托纵坐标
    
    返回
    ----------
    lng: number 经度
    lat: number 纬度
    
    """
    mc2ll = None
    
    for i in range(len(MCBAND)):
        if y >= MCBAND[i]:
            mc2ll = MC2LL[i]
            break
    lng, lat = convertor(x, y, mc2ll)
    
    return lng, lat
    
    
def mercator2px_bd(x, y, z): # 
    """百度地图 墨卡托坐标->像素坐标
    
    参数
    ----------
    x, y, z: number 墨卡托横纵坐标及缩放层级
    
    返回
    ----------
    x_px, y_px: number 像素横纵坐标
    
    
    """
    x_px = math.floor(x * pow(2, z-18))
    y_px = math.floor(y * pow(2, z-18))
    return x_px, y_px


def px2tile(x, y): 
    """像素坐标->瓦片坐标
    
    参数
    ----------
    x, y: number 像素坐标
    
    返回
    ----------
    x, y: number 瓦片坐标
    """
    x = int(math.floor(x/TILE_PIXEL_UNIT))
    y = int(math.floor(y/TILE_PIXEL_UNIT))
    return x, y


def ll2tile_bd(lng, lat, z):
    """百度地图 经纬度坐标->瓦片坐标
    
    参数
    ----------
    lng, lat: number 经纬度坐标
    z: 缩放层级
    
    返回
    ----------
    x, y: number 瓦片坐标
    """
    point = ll2mercator_bd(lng, lat) # 经纬度-->墨卡托坐标
    px = mercator2px_bd(point[0], point[1], z) # 墨卡托坐标-->像素坐标
    x, y = px2tile(px[0], px[1]) # 像素坐标-->瓦片坐标

    del point
    del px

    return x, y
    
def ll2tile_amap(lng, lat, z)
    """高德地图 经纬度坐标-->瓦片坐标
    
    摘要
    ----------
    具体计算过程的介绍可参照: [https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames]
    
    参数
    ----------
    lng, lat: number 经纬度坐标
    z: 缩放层级
    
    返回
    ----------
    x, y: number 瓦片坐标
    
    """
    
      lat_rad = math.radians(lat)
      n = 2.0 ** z
      x = int((lon + 180.0) / 360.0 * n)
      y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n) + 1
      return x, y
      
def get_save_path(TILES_DIR, x, y, z): 
    """获取瓦片存储绝对路径 会对瓦片的前继路径进行检查 如果发现无上级文件夹 会进行创建 最后返回瓦片的存储地址
    
    摘要
    ----------
    瓦片的组织方式为TILES_DIR/z/x/y.jpg
    
    参数
    ----------
    TILES_DIR: str 主目录 存储瓦片的根目录
    x, y, z: number 瓦片的横纵坐标及缩放层级
    
    返回
    ----------
    y_file: str 瓦片的存储路径
    
    """
    z_str = str(z)
    x_str = str(x)
    y_name = '%d.jpg' % y

    z_dir = os.path.join(TILES_DIR, z_str)
    if not os.path.exists(z_dir):
        os.mkdir(z_dir)
    x_dir = os.path.join(z_dir, x_str)
    if not os.path.exists(x_dir):
        os.mkdir(x_dir)
    y_file = os.path.join(x_dir, y_name)

    del z_str
    del x_str
    del y_name
    del z_dir
    del x_dir

    return y_file
    
def get_xyz_bd(start_zoom, end_zoom, left_bottom, right_top):
    """百度地图 获取所有的瓦片下载链接
    
    参数
    ----------
    start_zoom, end_zoom: number 起始层级和终止层级
    left_bottom, right_top: number 采集区域的左下角和右上角经纬度坐标
    
    返回
    ----------
    xyz_list: list 瓦片下载列表 前三列为x, y, z 第4列为瓦片标签 主要是为了支持断点续传
    
    """
    
    # 瓦片标签初始化
    tile_index = 0
    xyz_list = []
    for z in range(start_zoom, end_zoom+1):
        if z==start_zoom:
            x_lb, y_lb = ll2tile_bd(left_bottom[0], left_bottom[1], z)
            x_rt, y_rt = ll2tile_bd(right_top[0], right_top[1], z)
        else:
            # 四叉树 下一子树直接在上面基础上乘以2
            x_lb, y_lb = x_lb*2, y_lb*2
            x_rt, y_rt = x_rt*2+1, y_rt*2+1
        for x in range(x_lb, x_rt+1):
            for y in range(y_lb, y_rt+1):
                xyz_list.append([x, y, z, tile_index])
                tile_index += 1
    return xyz_list
    
def get_xyz_amp(start_zoom, end_zoom, left_top, right_bottom):
    """高德地图 获取所有的瓦片下载链接
    
    参数
    ----------
    start_zoom, end_zoom: number 起始层级和终止层级
    left_top, right_bottom: number 采集区域的左上角和右下角经纬度坐标
    
    返回
    ----------
    xyz_list: list 瓦片下载列表 前三列为x, y, z 第4列为瓦片标签 主要是为了支持断点续传
    
    """
    
    # 瓦片标签初始化
    tile_index = 0
    xyz_list = []
    for z in range(start_zoom, end_zoom+1):
        if z==start_zoom:
            x_lt, y_lt = ll2tile_amap(left_top[0], left_top[1], z)
            x_rb, y_rb = ll2tile_amap(right_bottom[0], right_bottom[1], z)
        else:
            # 四叉树 下一子树直接在上面基础上乘以2
            x_lt, y_lt = x_lt*2, y_lt*2-1
            x_rb, y_rb = x_rb*2+1, y_rb*2
        for x in range(x_lt, x_rb+1):
            for y in range(y_lt, y_rb+1):
                xyz_list.append([x, y, z, tile_index])
                tile_index += 1
    return xyz_list
    
def set_params(params, x, y, z, mode=1):
    """设置瓦片请求的params
    
    参数
    ----------
    params: dict 原始的params
    x, y, z: number 瓦片坐标
    mode: int 地图模式 1 代表非百度卫星图 2代表百度卫星图 默认参数为1
    
    返回
    ----------
    params: dict 完成设置的params 
    
    请求失败则打印错误信息,返回False
    """
    
    if mode == 1:
        params['x'] = str(x)
        params['y'] = str(y)
        params['z'] = str(z)
    elif mode == 2:
        u_str = 'x=' + str(x) + ';y=' + str(y) + ';z=' + str(z) + ';v=009;type=sate'
        params['u'] = u_str 
    else:
        print 'mode参数只能为1或2, 1代表非百度卫星图, 2代表百度卫星图!'
        return False
    return params
        
    