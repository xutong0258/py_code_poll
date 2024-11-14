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

import readFile

from common.mylogger import my_log
from component.ai_sport import *
from component.mysql import Mysql
from common.contants import *


class Run_50M_Free():
    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.rtsp_url_1 = cfg_dict['rtsp_url_1']

        self.rtsp_url_2 = cfg_dict['rtsp_url_2']
        self.ffmpeg_2 = None

        self.rtsp_url_3 = cfg_dict.get ('rtsp_url_3', None)
        if ENV == 'Linux':
            self.video_path_dir = cfg_dict['video_path_dir_linux']
        else:
            self.video_path_dir = eval(cfg_dict['video_path_dir_win'])
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)

        # self.ai_sport.reset_kafka_to_lastest()

        self.mysql.update_sql (sql_list)
        return


    def send_run_msg(self, size_m):
        # must assert
        topic = 'se_voice'
        key_words = ['"audioType":"ready"', f'"projectType":{self.project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=10)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')

        # must assert
        topic = 'se_voice'
        key_words = ['"audioType":"start"', f'"projectType":{self.project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=10)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')

        # TimeStartToRun
        file = os.path.join(self.path_dir, 'TimeStartToRun.yaml')
        self.ai_sport.send_msg_by_yaml_file(file, self.task_content_id, need_wait=False)

        topic = self.result_dic.get ('topic', 'se_voice')
        result_msg = self.result_dic.get ('result_msg', None)

        if result_msg:
            key_words = result_msg
            result = self.ai_sport.get_kafka_message_or(key_words=key_words, topic=topic, timeout=int(size_m), project_id=self.project_id)
            self.test_result = 'FAIL'
            if result:
                self.test_result = 'PASS'
            else:
                self.test_result = 'FAIL'


        return

    def run_one_loop(self):
        total_list = os.listdir (self.video_path_dir)

        for file_name in total_list:
            # self.mysql.set_test_project_db (proj_name=self.project_name, is_disabled=0, is_free_mode=True)
            if '.mp4' not in file_name:
                continue
            # print(f'file_name:{file_name}')
            my_log.info(f'file_name:{file_name}')
            file_name = os.path.join(self.video_path_dir, file_name)
            self.ffmpeg_1 = start_fake_camera_simple(file_name, whole_rtsp=self.rtsp_url_1, is_loop=True)

            file_name_2 = file_name
            file_name_2 = file_name_2.replace('start_1', 'start_2')
            my_log.info (f'file_name_2:{file_name_2}')
            self.ffmpeg_2 = start_fake_camera_simple(file_name_2, whole_rtsp=self.rtsp_url_2, is_loop=True)

            file_name_3 = file_name
            file_name_3 = file_name_3.replace('start_1', 'over')
            my_log.info (f'file_name_3:{file_name_3}')
            self.ffmpeg_3 = start_fake_camera_simple(file_name_3, whole_rtsp=self.rtsp_url_3, is_loop=True)
            self.ai_sport.reset_kafka_to_lastest ()

            size = os.path.getsize(file_name_3)
            # print (f"File size: {size} bytes")

            size_m = size / (1024 * 1024)
            size_m = int (size_m)
            # print (f"File size: {size_m} Mbytes")

            self.send_run_msg(size_m=size_m)

        return

    def test_run(self, open_dict, result_dic, pre_check=False):
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        project_id = self.ai_sport.config(project_name=self.project_name)
        self.project_id = project_id
        self.result_dic = result_dic

        # close project
        self.locationId = open_dict.get ('locationId', None)
        self.ai_sport.close_free_mode(self.locationId, project_id)

        # open
        self.locationId = open_dict.get ('locationId', None)
        task_content_id = self.ai_sport.open_proj_by_dict(open_dict, need_wait=False)
        self.task_content_id = task_content_id

        my_log.info (f'TEST_MODE:{TEST_MODE}')
        while True:
            self.run_one_loop()

        return

    def tearDown(self) -> None:
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        if self.ffmpeg_2:
            self.ffmpeg_2.stop()
        if self.ffmpeg_3:
            self.ffmpeg_3.stop()

        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1, is_free_mode=True)
        # 第十八步：退出AI智能体育项目
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")
        return

if __name__ == '__main__':
    pass
