> 本文主要介绍如何利用Python的requests库实现学校教务处网站的模拟登陆。关于教务处网站模拟登陆的典型应用主要有课程格子、超级课程表等，教务处网站形式多种多样，但登陆的基本流程类似，即构建表单-提交表单-实现登陆。本文以我浙的教务处网站为例进行模拟登陆演示。

## 登陆流程分析

首先打开我浙的教务处网站首页，F12打开开发者工具，输入学号、用户名、验证码，点击登陆之后，通过开发者工具可以看到，登陆过程包含3次请求，其中2次为暂时重定向(请求返回值为302代表暂时重定向)。

![登陆流程](http://p3f66obex.bkt.clouddn.com/14-1.JPG)

### 表单分析

点击'Headers',如下图所示，易得第一次请求为表单提交(POST提交)。

![第一次请求](http://p3f66obex.bkt.clouddn.com/14-2.JPG)

提交的表单如下：

![提交的表单](http://p3f66obex.bkt.clouddn.com/14-3.JPG)

其中username, password, authcode分别为学号、密码和验证码，后面的lt, execution, _eventld为表单隐藏值，表单隐藏值是反爬虫的初级手段，那么如何获取表单隐藏值呢？

### 获取表单隐藏值

表单隐藏值可以在实际登陆前，通过登陆界面表单填写部分的HTML代码获取，由下图所示：

![表单隐藏值](http://p3f66obex.bkt.clouddn.com/14-4.JPG)

可以看到，在登陆按钮的HTML源代码部分有3项隐藏的Input，观察name和value值，显然就是第一次请求POST的表单隐藏值。

### 获取3次请求的网址

- 第一次请求的网址为固定的，即'https://grs.zju.edu.cn/cas/login?locale=zh_CN&service=http%3A%2F%2Fgrs.zju.edu.cn%2Fallogene%2Fpage%2Fhome.htm%3Flocale=zh_CN'；

- 按照上述分析构造表单，模拟POST请求，返回的'Response Headers'的Location即为第二次请求的网址；

![重定向网址1](http://p3f66obex.bkt.clouddn.com/14-5.JPG)

- 同样的方式获取第三次请求的网址；

![重定向网址2](http://p3f66obex.bkt.clouddn.com/14-8.JPG)

- 访问第3次请求的网址，即可实现登陆，返回登陆之后的HTML代码。

![实现登陆](http://p3f66obex.bkt.clouddn.com/14-7.JPG)

## 代码实现(Python2.7)

### 导入相关包

```
import requests  # 导入requests
import os
from bs4 import BeautifulSoup  # 导入bs4中的BeautifulSoup
import time
from PIL import Image
```

### 实现第一次请求

```
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
```

> ** 需要注意的是：在访问的过程中，因为涉及多次请求，一定要通过Session()的方式来保持网站的对话。 **

log_html为访问教务处网站主页返回的html文档，HTML文档的解析包挺多的，这里我们选用BeautifulSoup来解析返回文档，获取表单隐藏值。

```
log_Soup = BeautifulSoup(log_html, 'lxml')
submit_list = log_Soup.find('li', class_='mt10 pl10').find_all('input')
item_list = []
for input_item in submit_list:
    item_list.append([input_item['name'], input_item['value']])
log_data = dict(item_list)
```

获取验证码图片，进行验证码识别，验证码识别可以采用OCR方式或者机器学习的方法，这里我们简化一下，直接采用手动输入的方式。

```
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
```

构建好表单后，即可实现第一次请求：

```
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
```

** 需要注意保存每一次请求的cookies，以保持登陆状态。**

### 第二次请求

```
# 第一次重定向
home_first_url = response_headers['Location']
# session_1 = requests.Session()
response_1 = session.get(url = home_first_url, headers = log_headers, cookies = cookies, allow_redirects=False)
response_headers_1 = dict(response_1.headers)
cookies_1 = response_1.cookies.get_dict() # 用于第二次重定向
```

### 第三次请求

```
# 第二次重定向
home_second_url = response_headers_1['Location']
response_2 = session.get(url = home_second_url, headers = log_headers, cookies = cookies_1)
cookies_2 = response_2.cookies.get_dict()
final_html = response_2.text # 登陆之后返回的html文档
```

至此，大功告成，成功登陆教务处网站。

下面就可以做一些有意思的事情了，比如利用flask封装一个API接口，进而做出课程表查询、考试提醒、成绩查询等各种功能型应用。





