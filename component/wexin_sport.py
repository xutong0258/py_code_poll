# coding=utf-8

import os
import sys
import json
import time
import unittest

from retry import retry

from common.handle_request import HandleRequest

from common.mylogger import my_log
from common.rtsp import *
from component.kafka_client import KafkaClient
import readFile

from component.mysql import Mysql
from common.contants import *



class We_Xin_Sport:
    def __init__(self) -> None:
        self.token = ""
        self.http = HandleRequest()
        return




    def login(self):
        my_log.info("第一步：老师登录AI智能操场平台")
        url = f"{we_xin_hot}/api/yskj-user/appApi/login"
        res = self.http.send(url=url, method="post", json=LOGIN_DATA)
        assert res.status_code == 200

        f_1 = 'login.txt'
        f_1 = os.path.join(LOG_DIR, f_1)
        readFile.dump_file(f_1, res.json())

        self.token = "Bearer " + res.json()['data']['token']

        return res.json(), self.token


    def logout(self):
        my_log.info("老师退出AI智能操场平台")

        headers = {"Authorization": self.token}
        url = f"{we_xin_hot}/api/logoutXf"
        res = self.http.send(url=url, method="get", headers=headers)

        f_1 = 'logout.txt'
        f_1 = os.path.join(LOG_DIR, f_1)
        readFile.dump_file(f_1, res)

        return

    def get_plat_Token(self):
        my_log.info("第二步：班级名单测试-查询开启项目列表")
        headers = {"Authorization": self.token}
        url = f"{we_xin_hot}/api/yskj-user/appApi/user/getByPhone?phonenumber=13655557903"
        res = self.http.send(url=url, method="get", headers=headers)
        # 后面接口用到：项目id
        f_1 = 'plat_Token.txt'
        f_1 = os.path.join(LOG_DIR, f_1)
        readFile.dump_file(f_1, res.json())

        self.plat_Token = res.json()['data']['user']['platToken']

        my_log.info (f'plat_Token:{self.plat_Token}')
        return self.plat_Token

    def get_task_Token(self):
        headers = {"Authorization": self.plat_Token}
        # url = f"https://dev-mini-program.tiyudata.com/api/ssoLogin"
        url = f"http://{TEST_SERVER}/api/ssoLogin"

        login_data = {"platCode":"yskj", "platToken":f"{self.plat_Token}"}
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        # res = self.http.send (url=url, method="post", json=login_data)
        res = self.http.send (url=url, method="post", json=login_data, headers=headers)
        # 后面接口用到：项目id
        f_1 = 'task_Token.txt'
        f_1 = os.path.join(LOG_DIR, f_1)
        readFile.dump_file(f_1, res.json())

        task_Token = res.json ()['data']['token']
        my_log.info (f'task_Token:{task_Token}')

        return task_Token

if __name__ == '__main__':
    obj = We_Xin_Sport()
    obj.login()
    obj.get_plat_Token()
    obj.get_task_Token()
    # obj.logout()


