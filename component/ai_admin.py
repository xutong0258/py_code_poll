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


class Admin:
    def __init__(self) -> None:
        self.token = ""
        self.http = HandleRequest()
        self.bootstrap_servers = BOOT_STRAP_SERVER
        self.voice_topic = VOICE_TOPIC
        self.real_time_topic = REAL_TIME_TOPIC
        self.ip = WEB_IP
        return

    def login(self):
        my_log.info("第一步：老师登录AI智能操场平台")
        url = f"{self.ip}/api/adminLogin"
        res = self.http.send(url=url, method="post", json=LOGIN_DATA)
        assert res.status_code == 200
        self.token = "Bearer " + res.json()['token']

        return res.json(), self.token

    def get_project_list(self):
        my_log.info("第二步：班级名单测试-查询开启项目列表")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/project/listAll?pageNum=1&pageSize=50&name=&frequency=&unit=&digit=&score=&isGrouping=&type="
        res = self.http.send(url=url, method="get", headers=headers)
        # 后面接口用到：项目id
        f_1 = 'project_list.txt'
        readFile.dump_file(f_1, res.json()['rows'])

        return res.json()

    def logout(self):
        my_log.info("老师退出AI智能操场平台")
        # stop_fake_camera()
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/logoutXf"
        res = self.http.send(url=url, method="get", headers=headers)
        return res.json()


if __name__ == '__main__':
    admin = Admin()
    admin.login()
    admin.get_project_list()
    admin.logout()

