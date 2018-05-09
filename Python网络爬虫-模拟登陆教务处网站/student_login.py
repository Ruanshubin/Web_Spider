# 导入相关包
import requests  #导入requests
from bs4 import BeautifulSoup  #导入bs4中的BeautifulSoup
import os
import csv
import time
from PIL import Image

log_url = 'https://grs.zju.edu.cn/cas/login?locale=zh_CN&service=http%3A%2F%2Fgrs.zju.edu.cn%2Fallogene%2Fpage%2Fhome.htm%3Flocale=zh_CN'

log_headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control':'max-age=0',
               'Connection':'keep-alive',
               'Host':'grs.zju.edu.cn',
               'Upgrade-Insecure-Requests':'1',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'             
               }
session = requests.Session()
log_html = session.get(url = log_url, headers = log_headers).text

# 获取data的属性值
log_Soup = BeautifulSoup(log_html, 'lxml')
submit_list = log_Soup.find('li', class_='mt10 pl10').find_all('input')
item_list = []
for input_item in submit_list:
    item_list.append([input_item['name'], input_item['value']])
log_data = dict(item_list)

# 获取验证码
auth_jpg_url = 'https://grs.zju.edu.cn/cas/Kaptcha.jpg'
picture = session.get(url = auth_jpg_url, headers = log_headers).content
auth_jpg = open('Kaptcha.jpg', 'wb')
auth_jpg.write(picture)
auth_jpg.close()

# 展示验证码
log_img = Image.open('Kaptcha.jpg')
log_img.show()

# 输入验证码
authcode = raw_input('Please input authcode: ')
log_data['authcode'] = authcode


# 教务处系统模拟登陆

data = {'username':'******',
        'password':'******',
        'authcode':log_data['authcode'],
        'submit':'',
        'lt':log_data['lt'],
        'execution':log_data['execution'],
        '_eventId':log_data['_eventId']
        }
        
# 实际登陆
response = session.post(url = log_url, data = data, headers = log_headers, allow_redirects=False)
response_headers = dict(response.headers)
cookies = response.cookies.get_dict() # 用于第一次重定向

# 第一次重定向
home_first_url = response_headers['Location']
# session_1 = requests.Session()
response_1 = session.get(url = home_first_url, headers = log_headers, cookies = cookies, allow_redirects=False)
response_headers_1 = dict(response_1.headers)
cookies_1 = response_1.cookies.get_dict() # 用于第二次重定向

# 第二次重定向
home_second_url = response_headers_1['Location']
response_2 = session.get(url = home_second_url, headers = log_headers, cookies = cookies_1)
cookies_2 = response_2.cookies.get_dict()
final_html = response_2.text # 登陆之后返回的html文档