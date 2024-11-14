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

BOOT_STRAP_SERVER = eval(ENV_DICT.get('BOOT_STRAP_SERVER', None))
# print (f'BOOT_STRAP_SERVER:{BOOT_STRAP_SERVER}')

NOTIFY_TOPIC = ENV_DICT.get('NOTIFY_TOPIC', None)
REAL_TIME_TOPIC = ENV_DICT.get('REAL_TIME_TOPIC', None)
VOICE_TOPIC = ENV_DICT.get('VOICE_TOPIC', None)
SE_TASK = ENV_DICT.get('SE_TASK', None)

class AiSport:
    def __init__(self, project_name=None) -> None:
        my_log.info (f'AiSport,project_name:{project_name}')
        self.token = ""
        self.http = HandleRequest()
        self.bootstrap_servers = BOOT_STRAP_SERVER
        self.voice_topic = VOICE_TOPIC
        self.real_time_topic = REAL_TIME_TOPIC
        self.ip = WEB_IP
        return

    def send_kafka_msg(self, topic, msg):
        my_log.info(f'发送kafka消息:{msg}')
        client = None
        try:
            my_log.info("连接kafka服务的地址bootstrap_servers：{}".format(self.bootstrap_servers))
            my_log.info("发送kafka消息的topic：{}".format(topic))
            client = KafkaClient(bootstrap_server=self.bootstrap_servers, topic=topic)
            res = client.send_message(message=msg, timeout=15)
            my_log.info(f'res:{res}')
        finally:
            if client:
                client.close()
                pass

        return

    def get_kafka_message(self, topic, timeout=300, key_words=[]):
        """
        获取kafka的一条消息，逐个过滤。
        :param topic: topic
        :param timeout: 超时时间 秒
        :param key_words: 列表，空不过滤。非空的话会用这个列表的字符串和kafka一条消息过滤
                          如果全部匹配返回该消息，否则继续等待
        :return:
        """

        client = None
        try:
            my_log.info("连接kafka服务的地址bootstrap_servers：{}".format(self.bootstrap_servers))
            my_log.info("获取kafka消息的topic：{}".format(topic))
            client = KafkaClient(bootstrap_server=self.bootstrap_servers, topic=topic)
            wait_seconds = 0
            while True:
                my_log.info(f"获取kafka消息列表key_words：{key_words}, topic:{topic}")
                res = client.receive_message(timeout=1, max_records=1)
                my_log.info(f'receive_message:{res}')
                time.sleep(1)
                wait_seconds += 1
                # 超时退出轮询kafka消息
                if wait_seconds > timeout:
                    my_log.warning("获取kafka消息超时")
                    break
                if not res:
                    my_log.info(f"没查到消息进入下一次轮询,超时时间{wait_seconds}s/{timeout}s")
                    continue
                # 查到了消息
                find = True
                for key_word in key_words:
                    if key_word not in res[0]:
                        find = False
                        break
                # 通过筛选确认是自己的消息
                if find:
                    return res[0]
        finally:
            if client:
                client.close()


    def get_kafka_message_or(self, topic, timeout=300, key_words=[], project_id=None):
        """
        获取kafka的一条消息，逐个过滤。
        :param topic: topic
        :param timeout: 超时时间 秒
        :param key_words: 列表，空不过滤。非空的话会用这个列表的字符串和kafka一条消息过滤
                          如果全部匹配返回该消息，否则继续等待
        :return:
        """

        client = None
        try:
            my_log.info("连接kafka服务的地址bootstrap_servers：{}".format(self.bootstrap_servers))
            my_log.info("获取kafka消息的topic：{}".format(topic))
            client = KafkaClient(bootstrap_server=self.bootstrap_servers, topic=topic)
            wait_seconds = 0
            prj_msg = f'"projectType":{project_id}'
            while True:
                my_log.info(f"获取kafka消息列表key_words:{key_words}, {prj_msg}")
                res = client.receive_message(timeout=1, max_records=1)
                my_log.info(f'receive_message:{res}')
                time.sleep(1)
                wait_seconds += 1
                # 超时退出轮询kafka消息
                if wait_seconds > timeout:
                    my_log.warning("获取kafka消息超时")
                    break
                if not res:
                    my_log.info(f"没查到消息进入下一次轮询,超时时间{wait_seconds}s/{timeout}s")
                    continue
                # 查到了消息
                find = False
                for key_word in key_words:
                    if key_word in res[0] and prj_msg in res[0]:
                        find = True
                        break
                    else:
                        fine = False
                # 通过筛选确认是自己的消息
                if find:
                    return res[0]
        finally:
            if client:
                client.close()

    def receive_count_kafka_message(self, topic, timeout=300, key_words=[]):
        """
        获取kafka的一条消息，逐个过滤。
        :param topic: topic
        :param timeout: 超时时间 秒
        :param key_words: 列表，空不过滤。非空的话会用这个列表的字符串和kafka一条消息过滤
                          如果全部匹配返回该消息，否则继续等待
        :return:
        """
        client = None
        cheat_count = 0
        serialScore = 0
        try:
            my_log.info("连接kafka服务的地址bootstrap_servers：{}".format(self.bootstrap_servers))
            my_log.info("获取kafka消息的topic：{}".format(topic))
            client = KafkaClient(bootstrap_server=self.bootstrap_servers, topic=topic)
            wait_seconds = 0
            while True:
                # my_log.info("获取kafka消息列表key_words：{}".format(key_words))
                res = client.receive_message(timeout=1, max_records=1)
                my_log.info(f'receive_message:{res}')
                time.sleep(1)
                wait_seconds += 1
                # 超时退出轮询kafka消息
                if wait_seconds > timeout:
                    my_log.warning("获取kafka消息超时")
                    break
                if not res:
                    my_log.info(f"没查到消息进入下一次轮询,超时时间{wait_seconds}s/{timeout}s")
                    continue

                if '"audioType":"score"' in res[0]:
                    result_dict = eval (res[0])
                    serialScore = result_dict['serialScore']
                    serialScore = round (serialScore, 2)
                    my_log.info (f'serialScore:{serialScore}')
                    break

                if '"audioType":"cheat"' in res[0]:
                    # 通过筛选确认是自己的消息
                    cheat_count = cheat_count + 1
                    my_log.info (f'cheat_count:{cheat_count}')
                    # return res[0]
                    continue
        finally:
            if client:
                client.close()
            return cheat_count, serialScore

    def reset_kafka_to_lastest(self):
        my_log.info("丢弃kafka的旧消息")
        client = KafkaClient(bootstrap_server=self.bootstrap_servers, topic=self.voice_topic)
        try:
            # 读取99999个消息 全部丢掉,然后提交offset
            client.receive_message(timeout=10, max_records=99999, enable_print=False)
        finally:
            client.close()
        self.reset_kafka_to_lastest_by_topic(topic='se_notify')
        self.reset_kafka_to_lastest_by_topic(topic='real_time_notify')

        return

    def reset_kafka_to_lastest_by_topic(self, topic):
        my_log.info("丢弃kafka的旧消息")
        client = KafkaClient(bootstrap_server=self.bootstrap_servers, topic=topic)
        try:
            # 读取99999个消息 全部丢掉,然后提交offset
            client.receive_message(timeout=10, max_records=99999, enable_print=False)
        finally:
            client.close()


    def login(self):
        my_log.info("第一步：老师登录AI智能操场平台")
        url = f"{self.ip}/api/login"
        res = self.http.send(url=url, method="post", json=LOGIN_DATA)
        assert res.status_code == 200
        self.token = "Bearer " + res.json()['token']

        return res.json(), self.token

    def http_post(self, url, payload):
        """
        创建task 返回task_id
        :param payload: 请求体
        :return: task_id
        """
        headers = {"Authorization": self.token}

        f_1 = 'payload.txt'
        f_1 = os.path.join(LOG_DIR, f_1)
        # readFile.dump_file(f_1, payload)
        my_log.info(f'http_post:{url}')

        res = self.http.send(url=url, method="post", json=payload, headers=headers)
        # payload中参数取上面接口中：name projects_id  grade  class_id
        return res.json()


    def select_project_list(self):
        my_log.info("第二步：班级名单测试-查询开启项目列表")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/project/list"
        res = self.http.send(url=url, method="get", headers=headers)
        # 后面接口用到：项目id
        return res.json()

    def get_project_id(self, res_proj_list, name):
        project_id = None
        for item in res_proj_list:
            if item['name'] == name:
                project_id = item['id']
        if project_id is None:
            raise ValueError (f'project_id is None, please check project management')
        return project_id

    def config(self, project_name):
        # 查询开启项目列表
        # api/core/project/list
        res_proj_list = self.select_project_list()
        f_1 = 'res_proj_list.txt'
        f_1 = os.path.join(LOG_DIR, f_1)
        # readFile.dump_file(f_1, res_proj_list)
        res_proj_list = res_proj_list['rows']

        if '多人' in project_name:
            project_name = project_name.replace ('多人', '')
        if '计圈跑' in project_name:
            project_name = '计圈跑'
        if '定距跑' in project_name:
            project_name = '定距跑'

        # print(f'project_name:{project_name}')
        projectType = self.get_project_id(res_proj_list, project_name)
        my_log.info(f"projectType:{projectType}")
        assert(projectType is not None)
        return projectType

    def http_requst_get(self, url):
        headers = {"Authorization": self.token}
        res = self.http.send(url=url, method="get", headers=headers)
        # 后面接口用到：项目id
        return res.json()


    def search_grade_list(self):
        my_log.info("第三步：查询开启项目年级列表")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/search/listGrade?"
        res = self.http.send(url=url, method="get", headers=headers)
        # 后面接口用到：年级：name id
        return res.json()

    def search_list_class_by_grade(self, grade_id):
        my_log.info("根据默认年级查询班级")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/search/listClassByGrade?"
        params = {"gradeId": grade_id}
        res = self.http.send(url=url, method="get", params=params, headers=headers)
        # 后面接口用到：班级：name grade id
        res_json = res.json()
        return res_json

    def search_class_list(self, grade_id):
        my_log.info("第四步：选择需要测试班级")
        headers = {"Authorization": self.token}
        params = {"gradeId": grade_id}
        url = f"{self.ip}/api/core/search/listClassByGrade"
        res = self.http.send(url=url, method="get", params=params, headers=headers)
        # 后面接口用到：班级：name grade id
        res_json = res.json()
        return res_json

    def search_class_gender(self, class_id):
        my_log.info("第五步：选择对应班级的学生测试")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/search/hasSameSexCount/{class_id}/gender/2"
        res = self.http.send(url=url, method="get", headers=headers)
        return res.json()

    def select_task_content(self, task_id):
        my_log.info("第八步：查询开启任务详情")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/content/selectTaskContentVOById?taskId={task_id}"
        res = self.http.send(url=url, method="get", headers=headers)
        return res.json()

    @retry(tries=20, delay=5)
    def query_itemized_free_testing_student(self, task_id, project_id, task_content_id, check_style):
        my_log.info("查看[人脸识别测试]当前项目测试学生的信息")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/itemizedFree/queryItemizedFreeTestingStudentVOList"
        params = {"taskId": task_id, "projectId": project_id, "taskContentId": task_content_id,
                  "checkStyle": check_style}
        res = self.http.send(url=url, method="get", params=params, headers=headers)

        f_1 = 'query_itemized_free_testing_student.txt'
        f_1 = os.path.join(LOG_DIR, f_1)
        readFile.dump_file(f_1, res.json())
        student_num = res.json()['data'][0]['studentNum']  # ctrl alt L
        assert student_num is not None
        return student_num


    def task_schedule(self, task_id):
        my_log.info("第十七步：返回当前任务数据清单")
        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/core/content/taskSchedule"
        params = {"taskId": task_id}
        res = self.http.send(url=url, method="get", params=params, headers=headers)
        return res.json()

    def logout(self, project_id=None, test_mode='free_mode'):
        my_log.info(f'老师退出AI智能操场平台, project_id:{project_id}, test_mode:{test_mode}')

        headers = {"Authorization": self.token}
        url = f"{self.ip}/api/logoutXf"
        res = self.http.send(url=url, method="get", headers=headers)
        return res.json()

    def close_free_mode(self, locationId, project_id):
        my_log.info("自由模式的一键关闭按钮")

        file = os.path.join(COMMON_DIR, 'CloseProjFreeMode.yaml')

        close_dict = readFile.read_yaml_dict(file)
        close_dict.update({"locationId": locationId})
        close_dict.update({"projectType": project_id})
        self.close_proj_by_dict(close_dict)

        return

    def open_free_mode(self):
        my_log.info("自由模式的一键关闭按钮")
        headers = {"Authorization": self.token}
        free_data = {"freeModeStatus": 0}
        url = f"{self.ip}/api/core/freeMode/statusAll?freeModeStatus=0"
        res = self.http.send(url=url, method="put", data=free_data, headers=headers)
        return res.json()


    def send_msg_by_file(self, file, taskContentId=None, locationId=None):
        time.sleep(1)
        msg_dict = readFile.get_case_data_list(file)
        file_dump = file.replace('json', 'yaml')

        readFile.dump_file(file_dump, eval(msg_dict[0]))
        msg_dict = readFile.read_yaml_dict(file_dump)

        current_time = int(time.time() * 1000)
        msg_dict.update({"sendTime": current_time})

        if taskContentId:
            msg_dict.update({"taskContentId": taskContentId})
        if locationId:
            msg_dict.update({"locationId": locationId})
        msg = json.dumps(msg_dict)
        my_log.info(f'msg:{msg}')
        topic = SE_TASK
        self.send_kafka_msg(topic, msg)
        return

    def send_msg_by_yaml_file(self, file, taskContentId=None, apend_dic=None, need_wait=False):
        if need_wait:
            time.sleep(1)
        msg_dict = readFile.read_yaml_dict(file)

        current_time = int(time.time() * 1000)
        msg_dict.update({"sendTime": current_time})

        if taskContentId:
            msg_dict.update({"taskContentId": taskContentId})
        if apend_dic:
            msg_dict.update(apend_dic)

        msg = json.dumps(msg_dict)
        # my_log.info(f'msg:{msg}')
        topic = SE_TASK
        self.send_kafka_msg(topic, msg)
        return

    def open_proj_by_dict(self, msg_dict, test_mode='face_mode', need_wait=False):
        # time.sleep(1)
        current_time = int(time.time() * 1000)
        task_content_id = int (time.time() % 10000)

        msg_dict.update({"sendTime": current_time})
        if test_mode != 'free_mode':
            msg_dict.update ({"taskContentId": task_content_id})
            msg_dict.update ({"truthTaskContentId": task_content_id})
        msg_dict.update ({"messageId": current_time})

        msg = json.dumps(msg_dict)
        # my_log.info(f'msg:{msg}')
        topic = SE_TASK
        self.send_kafka_msg(topic, msg)

        # my_log.info(f'TEST_MODE:{TEST_MODE}')
        if need_wait:
            # "messageComment":"OpenProjAnswer"
            topic = 'se_notify'
            key_words = ['"messageComment":"OpenProjAnswer"']
            timeout = 15
            result = self.get_kafka_message (key_words=key_words, topic=topic, timeout=timeout)

        return task_content_id

    def close_proj_by_dict(self, msg_dict):
        current_time = int(time.time() * 1000)

        msg_dict.update({"sendTime": current_time})
        msg_dict.update({"messageId": current_time})

        msg = json.dumps(msg_dict)
        # my_log.info(f'msg:{msg}')
        topic = SE_TASK
        self.send_kafka_msg(topic, msg)

        time.sleep(1)
        return


if __name__ == '__main__':
    obj = AiSport()

    obj.login()
