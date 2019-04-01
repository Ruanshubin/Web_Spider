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
百度地图瓦片下载
"""

from maptiles_api import *
import requests
import random
import time
import threading
import Queue
    
def download_tile_simple(xyz_item, TILES_DIR, headers, map_mode='normal'):
    """下载单张瓦片
    
    参数
    ----------
    xyz_item: list 瓦片参数集合 包括x,y,z和瓦片编号
    TILES_DIR: str 主目录 存储瓦片的根目录
    headers: dict 请求头
    map_mode: 百度地图格式 'normal' 普通地图 'custom':定制地图 'satellite'
    
    """
    
    x = xyz_item[0]
    y = xyz_item[1]
    z = xyz_item[2] 
    tile_index = xyz_item[3] 
    # 设置请求的params
    params = set_param(params, x, y, z)
    # 随机选择服务器，避免爬虫被封
    host = baidu.base_url[map_mode]
    server_begin = int(baidu.server_begin[map_mode])
    server_num = int(baidu.server_num[map_mode])
    random_num = random.randint(server_begin, server_begin+server_num-1)
    pre_num = baidu.pre_num[pre_num]
    host_true = host.replace((pre_num + server_begin),(pre_num + str(random_num)))
    # 获取瓦片保存路径
    save_path = get_save_path(TILES_DIR, x, y, z)
    if os.path.exists(save_path):
        os.remove(save_path)
    # 获取瓦片
    f_in = requests.get(url=host_true, params=params, headers=headers)
    # 保存地图瓦片
    with open(save_path, 'wb') as f_out:
        f_out.write(f_in.content)

    del save_path
    del f_in
    
    print '%d, %d, %d的瓦片下载完成，编号为%d.'%(x, y, z, tile_index)
    
    # 设置休眠时间，避免爬虫被封
    # time.sleep(0.05)
    
def download_tiles(start_zoom, end_zoom, left_bottom, right_top, TILES_DIR, headers, map_mode='normal', start_index=0):
    """批量下载地图瓦片
    
    参数
    ----------
    start_zoom, end_zoom: number 起始层级和终止层级
    left_bottom, right_top: number 采集区域的左下角和右上角经纬度坐标
    TILES_DIR: str 主目录 存储瓦片的根目录
    headers: dict 请求头
    map_mode: 百度地图格式 'normal' 普通地图 'custom':定制地图 'satellite'
    start_index: int 瓦片的标签 由0开始 以支持断点续传

    """
    # 创建瓦片根目录
    if not os.path.exists(TILES_DIR):
        os.mkdir(TILES_DIR)   
        
    # 获取瓦片路径集合
    xyz_list = get_xyz_bd(start_zoom, end_zoom, left_bottom, right_top)
    # 选取开始点到最后的部分
    xyz_list = xyz_list[start_index:len(xyz_list)]
    
    for xyz_item in xyz_list:
        download_tile_simple(xyz_item, TILES_DIR, headers, map_mode='normal')
        
def fetch_tile(q, lock, xyz_item, TILES_DIR, headers, map_mode='normal'):
    """将download_tile_simple与队列和锁组成一个线程任务
    
    参数
    ----------
    q: 队列
    lock: 锁
    其他参数意义与download_tile_simple等同
    
    """
    lock.acquire()
    while True:
        try:
            # 非阻塞读取队列数据
            xyz_item = q.get_nowait()
        except Exception, e:
            print e
            break
        # print '当前运行的线程名为：%s'% threading.currentThread().name
        download_tile_simple(xyz_item, TILES_DIR, headers, map_mode='normal')
    lock.release()
    
def download_tiles_thread(start_zoom, end_zoom, left_bottom, right_top, TILES_DIR, headers, map_mode='normal', start_index=0):
    """批量下载地图瓦片(多线程版)
    
    参数
    ----------
    start_zoom, end_zoom: number 起始层级和终止层级
    left_bottom, right_top: number 采集区域的左下角和右上角经纬度坐标
    TILES_DIR: str 主目录 存储瓦片的根目录
    headers: dict 请求头
    map_mode: 百度地图格式 'normal' 普通地图 'custom':定制地图 'satellite'
    start_index: int 瓦片的标签 由0开始 以支持断点续传

    """
    # 创建瓦片根目录
    if not os.path.exists(TILES_DIR):
        os.mkdir(TILES_DIR)   
        
    # 获取瓦片路径集合
    xyz_list = get_xyz_bd(start_zoom, end_zoom, left_bottom, right_top)
    # 选取开始点到最后的部分
    xyz_list = xyz_list[start_index:len(xyz_list)]

    q = Queue.Queue()
    for xyz in xyz_list:
        q.put(xyz)
        
    start = time.time()
    
    lock = threading.Lock()
    
    thread_list = []
    for i in range(thread_num):
        t = threading.Thread(target=fetch_tile, args=(q, lock, xyz_item, TILES_DIR, headers, map_mode), name=("child_thread_" + str(i+1)))
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    end = time.time()
    print 'Done %s ' %  (end-start)
    
def test():
"""测试函数"""
    # 宜春市采集
    left_bottom = [114.300483,27.750387]
    right_top = [114.497104,27.864648]  
    # 荆州市采集
    left_bottom = [112.079368,30.233315]
    right_top = [112.386948,30.426331]
    headers = {
                'Accept':'image/webp,image/*,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'     
               }  
    TILES_DIR = 'JZ_Tiles'
    # 建立访问链接集，其包含所有要下载的瓦片链接
    start_zoom = 13
    end_zoom = 16
    thread_num = 4
    # 批量下载地图瓦片
    download_tiles_thread(start_zoom, end_zoom, left_bottom, right_top, TILES_DIR, headers, map_mode='normal', start_index=0)
