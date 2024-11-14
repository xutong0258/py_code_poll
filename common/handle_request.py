# coding=utf-8

import requests
from common.mylogger import my_log

"""
封装的目的：
封装的需求：
    发送post请求，，发送get请求，发送patch请求，
    代码中如何做到不同请求方式的接口去发送不同的请求
    加判断
"""


class HandleRequest:
    def send(self, url, method, params=None, data=None, json=None, headers=None, log_print=False):
        # 将请求的方法转换为小写
        my_log.info("请求的url: {}".format(url))
        my_log.info("请求的headers: {}".format(headers))
        method = method.lower()
        if method == "post":
            my_log.info("请求入参json：{}".format(json))
            http_res = requests.post(url=url, json=json, data=data, headers=headers)
        elif method == "put":
            http_res = requests.put(url=url, data=data, headers=headers)
        elif method == "get":
            my_log.info("请求入参params：{}".format(params))
            http_res = requests.get(url=url, params=params, headers=headers)
        else:
            http_res = requests.request(method=method, url=url, params=params, headers=headers)
        my_log.info("返回状态码：{}".format(http_res.status_code))
        if log_print:
            my_log.info("返回数据：{}".format(http_res.json()))
        return http_res


if __name__ == '__main__':
    # 登录接口地址
    login_url = "http://192.168.2.202/api/login"

    # 登录的参数
    login_data = {"loginName": "15168284827", "password": "Rio4827"}
    # 登录的请求头
    header = {
        "Content-Type": "application/json"
    }

    http = HandleRequest()
    res = http.send(url=login_url, method="post", json=login_data, headers=header)

    print(res.json())
    print(res.json()['token'])
