# coding: utf-8
# 2020/03 by florakl

import requests
import time
import numpy as np


def url_get(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"}
    html = requests.get(url, headers=headers, timeout=20)
    code = html.status_code
    if code == 200:
        res = html.json()
        return res
    else:
        # print('Status Code:', code)
        return None


def time_format(numarray):
    # 时间戳转换为年月日
    t = time.localtime(numarray)
    # f_t = time.strftime("%Y-%m-%d %H:%M:%S", t)
    f_t = time.strftime("%Y-%m-%d", t)
    return f_t


def data_sort(x, y):
    # 将两个数组按x的顺序同时排序
    a = np.array(x)
    b = np.array(y)
    sorted_indices = np.argsort(a)
    a1 = a[sorted_indices]
    b1 = b[sorted_indices]
    return a1.tolist(), b1.tolist()
