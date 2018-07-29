#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright 2018 Shubin Ruan <ruanshubin.top>
#   All rights reserved.
#   BSD license.
#
#
# Authors: Shubin Ruan <ruanshubin@hikvision.com>
# Created: 2018.07.27
#

"""
读取路网shp文件，生成DiGraph，计算节点间的KSP
"""

from itertools import islice
import networkx as nx
import shapefile 
import numpy as np
import pandas as pd


def shp2graph(file_name):
    """shp文件转为DiGraph
    
    参数
    ----------
    file_name: str shp文件的路径（相对或绝对） 如file_name = 'JingZhou//edges//edges.shp'
    
    返回
    ----------
    G: DiGraph 有向网络结构
    """
    
    G = nx.DiGraph()
    shape_obj = shapefile.Reader(file_name)
    lines_list = list(shape_obj.records())
    line_fields = shape_obj.fields
    columns = [example[0] for example in line_fields]
    del columns[0] # 第一项为fields标签，删除
    lines_df = pd.DataFrame(lines_list, columns = columns)
    # 遍历添加道路，oneway属性为True的添加两次（正、反）
    for i in range(lines_df.shape[0]):
        node_from = lines_df['from'][i]
        node_to = lines_df['to'][i]
        oneway = lines_df['oneway'][i]
        cost = lines_df['length'][i]
        if type(cost) != float:
            cost = float(cost)
        if oneway == 'True':
            G.add_edge(node_from, node_to, weight=cost)
        elif oneway == 'False':
            G.add_edge(node_from, node_to, weight=cost)
            G.add_edge(node_to, node_from, weight=cost)
        else:
            print '道路%d添加失败，请重新检查' %i
        # print '第%d条道路添加成功，望您知悉！' %i
    return G
    
def K_shortest_paths(G, source, target, K, weight=None):
    """K则最短路径算法
    
    参数
    ----------
    G: DiGraph 有向网络结构
    source: obj 起点
    target: obj 终点
    K: int 选取的路径数
    weight: str 权重的属性名 默认为'weight'
    
    返回
    ----------
    List: list 路径集合，路径长度由短到长排列
    """
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), K))
    
def sum_weight(G, path):
    """统计路径的weight和
    
    参数
    ----------
    G: DiGraph 构建好的有向网络结构
    path: list 单个路径中的点集合
    
    返回
    ----------
    weight_total: number 路径的weight和
    
    """
    weight_total = 0
    for i in range(len(path)-1):
        weight_total += float(G[path[i]][path[i+1]]['weight'])
    return weight_total
    
def test():
    """测试函数"""
    file_name = 'JingZhou//edges//edges.shp'
    G = shp2graph(file_name)
    source = '1091987146'   
    target = '1232620838'
    K_paths = K_shortest_paths(G, source, target, 50)
    for path in K_paths:
        weight_total = sum_weight(G, path)
        print '该路径的长度为%s米。' %(str(weight_total))
        
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright 2018 Shubin Ruan <ruanshubin.top>
#   All rights reserved.
#   BSD license.
#
#
# Authors: Shubin Ruan <ruanshubin@hikvision.com>
# Created: 2018.07.27
#

"""
读取路网shp文件，生成DiGraph，计算节点间的KSP
"""

# from itertools import islice
import networkx as nx
import shapefile 
import numpy as np
import pandas as pd
from operator import itemgetter


def shp2graph(file_name):
    """shp文件转为DiGraph
    
    参数
    ----------
    file_name: str shp文件的路径（相对或绝对） 如file_name = 'JingZhou//edges//edges.shp'
    
    返回
    ----------
    G: DiGraph 有向网络结构
    """
    
    G = nx.DiGraph()
    shape_obj = shapefile.Reader(file_name)
    lines_list = list(shape_obj.records())
    line_fields = shape_obj.fields
    columns = [example[0] for example in line_fields]
    del columns[0] # 第一项为fields标签，删除
    lines_df = pd.DataFrame(lines_list, columns = columns)
    # 遍历添加道路，oneway属性为True的添加两次（正、反）
    for i in range(lines_df.shape[0]):
        node_from = lines_df['from'][i]
        node_to = lines_df['to'][i]
        oneway = lines_df['oneway'][i]
        cost = lines_df['length'][i]
        if type(cost) != float:
            cost = float(cost)
        if oneway == 'True':
            G.add_edge(node_from, node_to, weight=cost)
        elif oneway == 'False':
            G.add_edge(node_from, node_to, weight=cost)
            G.add_edge(node_to, node_from, weight=cost)
        else:
            print '道路%d添加失败，请重新检查' %i
        # print '第%d条道路添加成功，望您知悉！' %i
    return G
    
def pre_path_remove(G, pre_path):
    """将前继路径的边删除，避免搜索得到的后继路径里出现前继路径的边
    
    参数
    ----------
    G: DiGraph 有向网络结构
    pre_path: 前继路劲
    
    返回
    ----------
    edges_removed: List 删除的路径集合
    """  
    edges_removed = []
    for i in range(len(pre_path)-1):
        source = pre_path[i]
        target = pre_path[i+1]
        try:
            weight = G[source][target]['weight']
            G.remove_edge(source, target)
            edges_removed.append([source, target, weight])
        except:
            pass
        try:
            weight = G[target][source]['weight']
            G.remove_edge(target, source)
            edges_removed.append([target, source, weight])
        except:
            pass
    return edges_removed
            
def K_shortest_paths(G, source, target, K, weight=None):
    """K则最短路径算法
    
    参数
    ----------
    G: DiGraph 有向网络结构
    source: obj 起点
    target: obj 终点
    K: int 选取的路径数
    weight: str 权重的属性名 默认为'weight'
    
    返回
    ----------
    A: list 路径集合，路径长度由短到长排列
    """
    
    distance, first_path = nx.bidirectional_dijkstra(G, source, target)
    
    A = [{'weight': distance, 'path': first_path}]
    B = []
    
    if not A[0]['path']:
        return A
        
    for k in range(1, K):
        for i in range(0, len(A[-1]['path'])-1):
            print k, i
            node_squr = A[-1]['path'][i]
            path_root = A[-1]['path'][:i+1]
    
            edges_removed = []
            for path_k in A:
                curr_path = path_k['path']
                print curr_path
                if len(curr_path) > i and path_root == curr_path[:i+1]:
                    try:
                        weight = G[curr_path[i]][curr_path[i+1]]['weight']
                        G.remove_edge(curr_path[i], curr_path[i+1])
                    except:
                        pass
                    edges_removed.append([curr_path[i], curr_path[i+1], weight])
            
            if i>0:
                pre_edges_removed = pre_path_remove(G, path_root)
                for item in pre_edges_removed:
                    if not (item in edges_removed):
                        edges_removed.append(item)
            print (str(edges_removed) + '------')
            distance, path_squr = nx.bidirectional_dijkstra(G, node_squr, target)
            if path_squr:
                path_total = path_root[:-1] + path_squr
                dist_total = nx.bidirectional_dijkstra(G, source, node_squr)[0] + distance
                next_item = {'weight': dist_total, 'path': path_total}
                if not (next_item in B):
                    B.append(next_item)
                    
            for edge in edges_removed:
                G.add_edge(edge[0], edge[1], weight = edge[2])
        if len(B):
            B = sorted(B, key=itemgetter('weight'))
            A.append(B[0])
            B.pop(0)
        else:
            break
    return A
    
    
def test():
    """测试函数"""
    file_name = 'JingZhou_all//edges//edges.shp'
    G = shp2graph(file_name)
    source = '1091987146'   
    target = '1232620838'
    K_paths = K_shortest_paths(G, source, target, 30)
    for i in range(len(K_paths)):
        path = K_paths[i]
        weight_total = sum_weight(G, path)
        print '第%d条路径为%s，长度为%s米。' %(i+1, str(path), str(weight_total))


