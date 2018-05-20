# -*- coding: utf-8 -*-

#   __
#  /__)  _  _     _   _ _/   _
# / (   (- (/ (/ (- _)  /  _)
#          /

__author__ = 'RuanShuBin'

__all__ = ['bus_data', 'database', 'df2shp', 'poi', 'topology_analysis', 'code_conver']

# 版本管理
from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__

# 导入包
from . import bus_data
from . import database
from . import df2shp
from . import topology_analysis
from . import poi
from . import code_conver

# 导入函数
from .database import MongoDB_login
from .df2shp import points_to_shp, lines_to_shp, polygon_to_shp
from .poi import get_part_poi, save_all_poi
from .topology_analysis import haversine, grid_cut, poly_max
from .bus_data import *
from .area_data import *
from .code_conver import item_code_conver, df_code_conver

# 公交数据
from .bus_data.save import save_stations, get_busline_names, save_buslines
from .bus_data.get_stations import get_stations, get_stations_cluster
from .bus_data.get_buslines import get_buslines

# 行政区划
from .area_data.get_distinct_data import get_distinct_attribute, save_polygon, get_polygon_df

# 居民小区数据
from .area_data.get_residential_data import save_residential, get_residential
