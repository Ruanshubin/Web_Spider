# -*- coding:utf-8 -*-

'编码转化'

__author__ = 'RuanShuBin'

import pandas as pd
import numpy as np

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
    