#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
import json
import os
import random
import re
import warnings
from base64 import b64encode

import requests
from  urllib import parse
from Crypto.PublicKey import RSA
# from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5


RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDC7kw8r6tq43pwApYvkJ5lalja
N9BZb21TAIfT/vexbobzH7Q8SUdP5uDPXEBKzOjx2L28y7Xs1d9v3tdPfKI2LR7P
AzWBmDMn8riHrDDNpUpJnlAGUqJG9ooPn8j7YNpcxCa1iybOlc2kEhmJn5uwoanQ
q+CA6agNkqly2H4j6wIDAQAB
-----END PUBLIC KEY-----"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36",
    "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14"
]
random_USER_AGENTS = random.choice(USER_AGENTS)

def add_url_params(url:str, params:dict):
    """手动给url加payload,避免request内部编码问题导致请求的url与实际url不对应

    Args:
        url (str): 网址
        params (dict): 参数

    Returns:
        url: 加上菜蔬的url
    
    Example:
        >>> params = {'a': 123, 'b': 'hhhh'}
        >>> add_url_params('www.baidu.com', params)
        www.baidu.com?a=123&b=hhhh
    """
    url += '?'
    for key, value in params.items():
        url += key + '=' + str(value) + '&'
    return url.strip('&') #删除最后的&

def url_encode(data:dict):
    """手动用url码表对数据进行编码并返回, 因为request内部编码可能会出现问题

    Args:
        data (dict): 

    Returns:
        data (str): 
        
    Example:
        >>> data = {'serInfo': {'area': '12-121-3-1-3-2', 'user-key': ' '}, 'cartExt': {'specialId': 1}}
        >>> url_encode(data)
        %7B%22serInfo%22:%7B%22area%22:%2212-121-3-1-3-2%22,%22user-key%22:%22%22%7D,%22cartExt%22:%7B%22specialId%22:1%7D%7D
    """
    data_str = parse.quote(str(data))
    data_str = data_str.replace('%27', '%22').replace('%3A', ':').replace('%20', '').replace('%2C',',').replace('False','false')
    return data_str

def response_status(resp):
    if resp.status_code != requests.codes.OK:
        print('Status: %u, Url: %s' % (resp.status_code, resp.url))
        return False
    return True


def save_image(resp, image_file):
    with open(image_file, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            f.write(chunk)
            
def open_image(image_file):
    if os.name == "nt":
        os.system('start ' + image_file)  # for Windows
    else:
        if os.uname()[0] == "Linux":
            if "deepin" in os.uname()[2]:
                os.system("deepin-image-viewer " + image_file)  # for deepin
            else:
                os.system("eog " + image_file)  # for Linux
        else:
            os.system("open " + image_file)  # for Mac



# def encrypt_pwd(password, public_key=RSA_PUBLIC_KEY):
#     rsa_key = RSA.importKey(public_key)
#     encryptor = Cipher_pkcs1_v1_5.new(rsa_key)
#     cipher = b64encode(encryptor.encrypt(password.encode('utf-8')))
#     return cipher.decode('utf-8')


def encrypt_payment_pwd(payment_pwd):
    return ''.join(['u3' + x for x in payment_pwd])




def parse_json(s):
    begin = s.find('{')
    end = s.rfind('}') + 1
    return json.loads(s[begin:end])


def get_tag_value(tag, key='', index=0):
    if key:
        value = tag[index].get(key)
    else:
        value = tag[index].text
    return value.strip(' \t\r\n')


def parse_items_dict(d):
    result = ''
    for index, key in enumerate(d):
        if index < len(d) - 1:
            result = result + '{0} x {1}, '.format(key, d[key])
        else:
            result = result + '{0} x {1}'.format(key, d[key])
    return result

def parse_sku_id(sku_ids:str):
    """将商品id字符串解析为字典

    商品id字符串采用英文逗号进行分割。
    可以在每个id后面用冒号加上数字，代表该商品的数量，如果不加数量则默认为1。

    Params
    ------
        sku_ids: 商品id字符串
        
    Return
    ------
        dict
        
    Examples
    --------
        >>> parse_sku_id('123456')
        {'123456': '1'}
        >>> parse_sku_id('123456,123789')
        {'123456': '1', '123789': '1'}
        >>> parse_sku_id('123456:1,123789:3')
        {'123456': '1', '123789': '3'}
        >>> parse_sku_id('123456:2,123789')
        {'123456': '2', '123789': '1'}
    
    """
    if isinstance(sku_ids, dict):  # 防止重复解析
        return sku_ids

    sku_id_list = list(filter(bool, map(lambda x: x.strip(), sku_ids.split(','))))
    result = dict()
    for item in sku_id_list:
        if ':' in item:
            sku_id, count = map(lambda x: x.strip(), item.split(':'))
            result[sku_id] = count
        else:
            result[item] = '1'
    return result


def parse_area_id(area:str):
    """解析地区id字符串:将分隔符替换为下划线 _
    
    Params
    ------
        area: 地区id字符串(使用 _ 或 - 分割)，如 '12_904_3375' 或 '12-904-3375'
        
    Returns
    -------
        str
        
    Examples
    --------
    >>> parse_area_id('12_904_3375')
    12_904_3375
    >>> parse_area_id('12-904-3375')
    12_904_3375
    
    """
    area_id_list = list(map(lambda x: x.strip(), re.split('_|-', area)))
    area_id_list.extend((4 - len(area_id_list)) * ['0'])
    return '_'.join(area_id_list)


def split_area_id(area):
    """将地区id字符串按照下划线进行切割，构成数组。数组长度不满4位则用'0'进行填充。
    :param area: 地区id字符串（使用 _ 或 - 进行分割），如 12_904_3375 或 12-904-3375
    :return: list
    """
    area_id_list = list(map(lambda x: x.strip(), re.split('_|-', area)))
    area_id_list.extend((4 - len(area_id_list)) * ['0'])
    return area_id_list


def deprecated(func):
    """This decorator is used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used.
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            stacklevel=2
        )
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func

# 弃用
def check_login(func):
    """用户登陆态校验装饰器。若用户未登陆，则调用扫码登陆"""

    @functools.wraps(func)
    def new_func(self, *args, **kwargs):
        if not self.is_login:
            print("{0} 需登陆后调用，开始扫码登陆".format(func.__name__))
            self.login_by_QRcode()
        return func(self, *args, **kwargs)

    return new_func

