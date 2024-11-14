# coding=utf-8

import os
import sys
import json
import time
import unittest
import warnings
import platform

file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)
base_name = os.path.basename(path_dir)

while 'se-autotest' not in base_name:
    path_dir = os.path.dirname(path_dir)
    base_name = os.path.basename(path_dir)

sys.path.append(path_dir)

from common.rtsp import *
import readFile

from common.mylogger import my_log
from component.ai_sport import *
from component.mysql import Mysql
from common.contants import *


class Rope_Skip_Face_Common():
    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = eval(cfg_dict['video_path_1'])
        self.video_path_2 = eval(cfg_dict['video_path_2'])
        self.whole_rtsp = cfg_dict.get ('rtsp_url_1', None)
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0)

        self.ai_sport.reset_kafka_to_lastest()
        self.mysql.update_sql(sql_list)
        return

    def do_run(self, project_id, task_content_id, result_dic):

        # send messageComment_startOff
        file = os.path.join(self.path_dir, 'messageComment_startOff.yaml')
        apend_dic = {"taskContentId": task_content_id,
                     "truthTaskContentId": task_content_id}
        self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

        # 断言 "audioType":"preStart"
        topic = 'se_voice'
        key_words = ['"audioType":"preStart"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=3)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info(f'score_voice:{result}')

        # 断言 "audioType":"start"
        topic = 'se_voice'
        key_words = ['"audioType":"start"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=3)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info(f'score_voice:{result}')

        # result check
        result_dict = {}
        result_list = []

        repeat_times = 1
        expect_core = result_dic.get ('expect_core', None)
        if expect_core:
            repeat_times = len (expect_core)
        topic = result_dic.get ('topic', 'se_voice')
        result_msg = result_dic.get ('result_msg', None)
        timeout = result_dic.get ('timeout', 70)
        reverse_flag = result_dic.get ('reverse_flag', False)

        key_words = [result_msg, f'"projectType":{project_id}']
        for index in range (repeat_times):
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int (timeout))
            my_log.info (f'result:{result}')
            if reverse_flag:
                if result:
                    self.test_result = 'FAIL'
                    break
                else:
                    self.test_result = 'PASS'
                    break
            else:
                if result:
                    result = eval (result)
                    self.test_result = 'PASS'
                else:
                    self.test_result = 'FAIL'
                    break

        self.test_mode = result_dic.get ('test_mode', 'face_mode')
        dict_para = {
            'project_name': self.project_name,
            'test_name': self.test_name,
            'test_result': self.test_result,
            'test_mode': f'{self.test_mode}'
        }

        readFile.update_result (LOG_DIR, dict_para)



        return

    def test_run(self, open_dict, result_dic):
        """
        随堂测试--人脸识别测试-正向业务流程
        """
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        project_id = self.ai_sport.config(project_name=self.project_name)
        self.project_id = project_id


        self.test_mode = result_dic.get ('test_mode', None)
        self.locationId = open_dict.get ('locationId', None)
        # close free mode must
        file = None
        if self.test_mode == 'free_mode':
            file = os.path.join(COMMON_DIR, 'CloseProjFreeMode.yaml')
        else:
            file = os.path.join(COMMON_DIR, 'CloseProjItemizedTest.yaml')

        close_dict = readFile.read_yaml_dict(file)
        close_dict.update({"locationId": self.locationId})
        close_dict.update ({"projectType": self.project_id})
        self.ai_sport.close_proj_by_dict(close_dict)

        # send open
        task_content_id = self.ai_sport.open_proj_by_dict (open_dict)

        # push video
        self.ffmpeg = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.whole_rtsp)

        # assert "messageComment":"faceAutoRecResult"
        topic = 'se_notify'
        key_words = ['"messageComment":"faceAutoRecResult"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=10)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info(f'score_voice:{result}')

        self.ffmpeg.stop ()
        # self.ai_sport.reset_kafka_to_lastest()
        self.ffmpeg = start_fake_camera_simple (self.video_path_2, whole_rtsp=self.whole_rtsp)

        self.test_result = 'FAIL'
        self.test_mode = 'face_mode'
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.do_run (project_id, task_content_id, result_dic)
        else:
            retry = 2
        for index in range(retry):
            my_log.info(f'retry:{retry}')
            self.do_run(project_id, task_content_id, result_dic)
            if self.test_result == 'PASS':
                break
        return

    def tearDown(self) -> None:
        # close free mode must
        file = None
        if self.test_mode == 'free_mode':
            file = os.path.join(COMMON_DIR, 'CloseProjFreeMode.yaml')
        else:
            file = os.path.join(COMMON_DIR, 'CloseProjItemizedTest.yaml')

        close_dict = readFile.read_yaml_dict(file)
        close_dict.update({"locationId": self.locationId})
        close_dict.update ({"projectType": self.project_id})
        self.ai_sport.close_proj_by_dict(close_dict)

        if self.ffmpeg:
            self.ffmpeg.stop()
        # 退出AI智慧平台
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1)
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass