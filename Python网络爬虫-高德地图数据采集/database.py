# -*- coding:utf-8 -*-

'数据库登录'

__author__ = 'RuanShuBin'

from pymongo import MongoClient

'mongo数据库'
# cmd启动服务
# mongod --dbpath=D:\MongoDB\data\db
# 另开cmd，mongo
# use bus_data
'''
db.createUser({
    "user":"hello",
    "pwd":"python",
    "roles":[{"role":"readWrite","db":"bank_data"}]
}   
)
'''

def MongoDB_login(dbName, collection, user='localhost', port=27017, auth_name=None, pwd=None):
    '''
    user:用户名
    port:端口号
    dbName:数据库名
    collection:表名
    '''
    client = MongoClient(user, port)
    db = client[dbName]
    if auth_name:
        db.authenticate(auth_name, pwd)
    col = db[collection]; # 连接集合
    return col