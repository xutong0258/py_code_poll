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



class Simple_Stress_Common():
    my_log.info("Stress_Common")
    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = eval(cfg_dict['video_path_1'])
        my_log.info (f'self.video_path_1:{self.video_path_1}')
        self.rtsp_url_1 = cfg_dict.get('rtsp_url_1', None)

        self.video_path_2 = cfg_dict.get('video_path_2', None)
        if self.video_path_2:
            self.video_path_2 = eval(self.video_path_2)
            self.rtsp_url_2 = cfg_dict.get('rtsp_url_2', None)

        self.video_path_3 = cfg_dict.get('video_path_3', None)
        if self.video_path_3:
            self.video_path_3 = eval(self.video_path_3)
            self.rtsp_url_3 = cfg_dict.get('rtsp_url_3', None)

        self.video_path_4 = cfg_dict.get ('video_path_4', None)
        if self.video_path_4:
            self.video_path_4 = eval(self.video_path_4)
            self.rtsp_url_4 = cfg_dict.get('rtsp_url_4', None)

        self.video_path_5 = cfg_dict.get ('video_path_5', None)
        if self.video_path_5:
            self.video_path_5 = eval(self.video_path_5)
            self.rtsp_url_5 = cfg_dict.get('rtsp_url_5', None)

        self.video_path_6 = cfg_dict.get ('video_path_6', None)
        if self.video_path_6:
            self.video_path_6 = eval(self.video_path_6)
            self.rtsp_url_6 = cfg_dict.get('rtsp_url_6', None)

        self.video_path_7 = cfg_dict.get ('video_path_7', None)
        if self.video_path_7:
            self.video_path_7 = eval(self.video_path_7)
            self.rtsp_url_7 = cfg_dict.get('rtsp_url_7', None)

        self.video_path_8 = cfg_dict.get ('video_path_8', None)
        if self.video_path_8:
            self.video_path_8 = eval(self.video_path_8)
            self.rtsp_url_8 = cfg_dict.get('rtsp_url_8', None)

        self.video_path_9 = cfg_dict.get ('video_path_9', None)
        if self.video_path_9:
            self.video_path_9 = eval(self.video_path_9)
            self.rtsp_url_9 = cfg_dict.get('rtsp_url_9', None)

        self.video_path_10 = cfg_dict.get ('video_path_10', None)
        if self.video_path_10:
            self.video_path_10 = eval(self.video_path_10)
            self.rtsp_url_10 = cfg_dict.get('rtsp_url_10', None)


        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)
        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)
        if sql_list:
            self.mysql.update_sql(sql_list)

        # self.ai_sport.reset_kafka_to_lastest()
        self.ffmpeg_2 = None
        return

    def run_one_loop(self):
        # push video
        self.ffmpeg_1 = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.rtsp_url_1, is_loop=False)

        if self.video_path_2:
            self.ffmpeg_2 = start_fake_camera_simple (self.video_path_2, whole_rtsp=self.rtsp_url_2, is_loop=False)

        if self.video_path_3:
            self.ffmpeg_3 = start_fake_camera_simple (self.video_path_3, whole_rtsp=self.rtsp_url_3, is_loop=False)

        if self.video_path_4:
            self.ffmpeg_4 = start_fake_camera_simple (self.video_path_4, whole_rtsp=self.rtsp_url_4, is_loop=False)

        if self.video_path_5:
            self.ffmpeg_5 = start_fake_camera_simple (self.video_path_5, whole_rtsp=self.rtsp_url_5, is_loop=False)

        if self.video_path_6:
            self.ffmpeg_6 = start_fake_camera_simple (self.video_path_6, whole_rtsp=self.rtsp_url_6, is_loop=False)

        if self.video_path_7:
            self.ffmpeg_7 = start_fake_camera_simple (self.video_path_7, whole_rtsp=self.rtsp_url_7, is_loop=False)

        if self.video_path_8:
            self.ffmpeg_8 = start_fake_camera_simple (self.video_path_8, whole_rtsp=self.rtsp_url_8, is_loop=False)

        if self.video_path_9:
            self.ffmpeg_9 = start_fake_camera_simple (self.video_path_9, whole_rtsp=self.rtsp_url_9, is_loop=False)

        if self.video_path_10:
            self.ffmpeg_10 = start_fake_camera_simple (self.video_path_10, whole_rtsp=self.rtsp_url_10, is_loop=False)
        return

    def test_run(self):
        """
        随堂测试--人脸识别测试-正向业务流程
        """
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        self.project_id = self.ai_sport.config(project_name=self.project_name)

        files = os.listdir(self.path_dir)
        total_list = []
        for item in files:
            if '.yaml' not in item or 'case_dict.yaml' in item:
                continue
            total_list.append(item)

        for item in total_list:
            file = os.path.join(self.path_dir, item)
            self.ai_sport.send_msg_by_yaml_file(file)

        while True:
            self.run_one_loop()
            my_log.info (f'run_one_loop done sleep')
            time.sleep(60)


        return

    def tearDown(self) -> None:
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        if self.ffmpeg_2:
            self.ffmpeg_2.stop()
        # 退出AI智慧平台
        self.ai_sport.logout(self.project_id, self.test_mode)
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass