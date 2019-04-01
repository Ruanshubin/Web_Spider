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
将XYZ型瓦片转换为ArcGIS瓦片
"""

import os
from xml.dom import minidom
from xml.dom import *
import shutil

def ten_sixteen(numStr):
    """十进制转十六进制
    
    参数
    ----------
    numStr: str 十进制数
    
    返回
    ----------
    result: str 十六进制数（不足8位以0补全）
    
    """
    num_sixteen_str = hex(int(numStr))[2::].upper()
    result = '0' * (8-len(num_sixteen_str)) + num_sixteen_str
    return result
 
def get_arc_path(tiles_dir, x, y, z):
    """获取ArcGIS瓦片存储路径 会对瓦片的前继路径进行检查 如果发现无上级文件夹 会进行创建 最后返回瓦片的存储地址
    
    摘要
    ----------
    ArcGIS与XYZ不同的是,其不是Z/X/Y的组织方式 它是Z/Y/X的组织架构,所以需要进行XY的互换
    
    参数
    ----------
    tiles_dir: str 主目录 存储瓦片的根目录
    x, y, z: number 瓦片的横纵坐标及缩放层级
    
    返回
    ----------
    x_file: str 瓦片的存储路径
    
    """
    
    z_str = 'L' + str(z)
    y_str = 'R' + ten_sixteen(str(2**(z-1) - y - 1 ))
    x_name = '%s.jpg' % ('C' + ten_sixteen(str(2**(z-1) + x)))

    z_dir = os.path.join(tiles_dir, z_str)
    if not os.path.exists(z_dir):
        os.mkdir(z_dir)
    y_dir = os.path.join(z_dir, y_str)
    if not os.path.exists(y_dir):
        os.mkdir(y_dir)
    x_file = os.path.join(y_dir, x_name)

    del z_str
    del y_str
    del x_name
    del z_dir
    del y_dir

    return x_file

def xyz2arc(xyz_dir, arcgis_dir):
    """将XYZ型瓦片转换为ArcGIS瓦片
    
    参数
    ----------
    xyz_dir: str 存储XYZ瓦片的地址
    arcgis_dir: str 存储ArcGIS瓦片的地址
    
    """
    
    # 建立arcgis瓦片文件夹
    if not os.path.exists(arcgis_dir):
        os.mkdir(arcgis_dir)
        
    z_strs = list(os.listdir(xyz_dir))
    for z_str in z_strs:
        z_dir = os.path.join(xyz_dir, z_str)
        x_strs = list(os.listdir(z_dir))
        for x_str in x_strs:
            x_dir = os.path.join(z_dir, x_str)
            y_strs = list(os.listdir(x_dir))
            for y_str in y_strs:
                z = int(z_str)
                y = int(y_str.split('.')[0])
                x = int(x_str)
                y_file = os.path.join(x_dir, y_str) # XYZ瓦片地址
                arcgis_url = get_arc_path(arcgis_dir, x, y, z) # ArcGIS瓦片的地址
                if not os.path.exists(arcgis_url):
                    # 将瓦片文件拷贝到目标文件夹
                    shutil.copy(y_file,  arcgis_url)
        print '%s层级瓦片生成成功！'%(z_str)

        
def make_conf_xml(start_zoom, end_zoom, file_name, DPI = 96):
    """生成配置文件conf.xml
    
    参数
    ----------
    start_zoom, end_zoom: int 起/终的缩放层级
    file_name: str 模板文件保存路径
    DPI: int 每英寸的像素数 默认取96
    
    """
  
    DOMTree = minidom.parse("conf_templet.xml")
    root_node = DOMTree.documentElement
    LODInfos_list = root_node.getElementsByTagName("LODInfo") # 返回List列表
    # 获取LODInfos节点
    LODInfos_node = LODInfos_list[0].parentNode
    # 获取模板
    LODInfo_templet = LODInfos_list[0].cloneNode('true')
    # 删除第一个LODInfo
    LODInfos_node.removeChild(LODInfos_list[0])
    
    # 添加到LODInfos_node之后
    for i in range(start_zoom, end_zoom+1):
        # 设置Zoom
        # 因为文本专门占一个dom，所以后面添加childNodes[0]
        LevelID_node = LODInfo_templet.getElementsByTagName("LevelID")[0].childNodes[0]
        LevelID_node.nodeValue = str(i)
        # 设置比例尺
        Scale_node = LODInfo_templet.getElementsByTagName("Scale")[0].childNodes[0]
        # DPI为每英寸的像素数，其中1英寸=0.0254米
        Resolution = 2**(18-i)
        Scale_node.nodeValue = str(DPI / 0.0254 * Resolution)
        # 设置分辨率
        Resolution_node = LODInfo_templet.getElementsByTagName("Resolution")[0].childNodes[0]
        Resolution_node.nodeValue = str(Resolution)
        # 添加节点
        LODInfos_node.appendChild(LODInfo_templet)
        LODInfo_templet = LODInfo_templet.cloneNode('true') # 必须复制一份，否则节点只能添加一次
    
    try:
        with open(file_name,'w') as fh:
        # writexml()第一个参数是目标文件对象，第二个参数是根节点的缩进格式，第三个参数是其他子节点的缩进格式，
        # 第四个参数制定了换行格式，第五个参数制定了xml内容的编码。
            DOMTree.writexml(fh, indent='', addindent='\t', newl='\n', encoding='UTF-8')
    except Exception as err:
        print('错误信息：{0}'.format(err))        


def make_conf_cdi(left_bottom, right_top, file_name):
    """生成配置文件conf.cdi
    
    参数
    ----------
    left_bottom, right_top: number 采集区域的左下角和右上角经纬度坐标
    file_name: str 模板文件保存路径
    
    """
    
    DOMTree = minidom.parse("conf_templet.cdi")
    root_node = DOMTree.documentElement
    X_Min_Value, Y_Min_Value = convert_coord_to_mercator(left_bottom[0], left_bottom[1])
    X_Max_Value, Y_Max_Value = convert_coord_to_mercator(right_top[0], right_top[1])
    # 设置相应值
    X_Min = root_node.getElementsByTagName('XMin')[0].childNodes[0]
    X_Min.nodeValue = str(X_Min_Value)
    Y_Min = root_node.getElementsByTagName('YMin')[0].childNodes[0]
    Y_Min.nodeValue = str(Y_Min_Value)
    X_Max = root_node.getElementsByTagName('XMax')[0].childNodes[0]
    X_Max.nodeValue = str(X_Max_Value)
    Y_Max = root_node.getElementsByTagName('YMax')[0].childNodes[0]
    Y_Max.nodeValue = str(Y_Max_Value)
    try:
        with open(file_name,'w') as fh:
            DOMTree.writexml(fh,indent='',addindent='\t',newl='\n',encoding='UTF-8')
    except Exception as err:
        print('错误信息：{0}'.format(err))                   

def test():
    """测试函数(宜春)"""
    
    # 参数配置
    left_bottom = [114.300483,27.750387]
    right_top = [114.497104,27.864648]
    start_zoom = 13
    end_zoom = 19
    DPI = 96
    file_str = 'YiChun_Tiles_BD'
    xyz_dir = 'tiles_yichun_13_18'
    
    if not os.path.exists(file_str):
        os.mkdir(file_str)
    Layders_str = os.path.join(file_str, 'Layers')
    if not os.path.exists(Layders_str):
        os.mkdir(Layders_str)
    alllayers_str = os.path.join(Layders_str, '_alllayers')
    if not os.path.exists(alllayers_str):
        os.mkdir(alllayers_str)
    conf_cdi_str = os.path.join(Layders_str, 'conf.cdi')
    conf_xml_str = os.path.join(Layders_str, 'conf.xml')
    make_conf_cdi(left_bottom, right_top, conf_cdi_str)
    print 'conf.cdi文件创建成功！'
    make_conf_xml(start_zoom, end_zoom, conf_xml_str, DPI)
    print 'conf.xml文件创建成功！'
    xyz2arc(xyz_dir, alllayers_str)
    print 'ArcGIS地图瓦片转换成功。'
