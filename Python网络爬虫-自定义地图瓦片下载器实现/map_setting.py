#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright 2018 Shubin Ruan <ruanshubin.top>
#   All rights reserved.
#   BSD license.
#
#
# Authors: Shubin Ruan <https://github.com/Ruanshubin>
# Created: 2018.07.27
#

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
         'server_begin':'0',
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
                }
        }