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



class Rope_Skip_Free_Common():
    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = eval(cfg_dict['video_path_1'])
        self.video_path_2 = cfg_dict.get('video_path_2', None)
        if self.video_path_2:
            self.video_path_2 = eval(self.video_path_2)

        # my_log.info (f'cfg_dict:{cfg_dict}')
        if ENV == 'Linux':
            self.video_path_dir = cfg_dict['video_path_dir_linux']
        else:
            self.video_path_dir = eval(cfg_dict['video_path_dir_win'])

        self.whole_rtsp = cfg_dict.get ('rtsp_url_1', None)
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)
        
        self.ai_sport.reset_kafka_to_lastest()
        self.mysql.update_sql(sql_list)
        return

    def run_one_file(self, file_name):
        # keep result
        result_file = os.path.join (LOG_DIR, 'rope_skip.yaml')

        self.ai_sport.reset_kafka_to_lastest ()
        self.ai_sport.close_free_mode (self.locationId, self.project_id)
        topic = 'se_notify'
        key_words = ['"messageComment":"CloseProjAnswer"']
        timeout = 5
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=timeout)

        # wait last close then open
        task_content_id = self.ai_sport.open_proj_by_dict (self.open_dict, need_wait=False)
        topic = 'se_notify'
        key_words = ['"messageComment":"OpenProjAnswer"']
        timeout = 10
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=timeout)

        # file_name = os.path.join (self.video_path_dir, dir_name, file_name)

        if ENV == 'Linux':
            pass
        else:
            file_name = file_name.replace ('/', '\\')

        # push video
        my_log.info ("开始推送视频")
        self.ffmpeg = start_fake_camera_simple (self.video_path_1, whole_rtsp=self.whole_rtsp)

        # 断言 se_voice "audioType":"ready"
        topic = 'se_voice'
        key_words = ['"audioType":"ready"', f'"projectType":{self.project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=20)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')

        # self.ffmpeg.stop ()
        # push video
        my_log.info ("开始推送视频")
        # self.ffmpeg = start_fake_camera_simple (self.video_path_2, is_loop=False, whole_rtsp=self.whole_rtsp)
        self.ffmpeg = start_fake_camera_simple (file_name, is_loop=False, whole_rtsp=self.whole_rtsp)

        time.sleep (60)
        self.ffmpeg = start_fake_camera_simple (self.video_path_1, whole_rtsp=self.whole_rtsp)

        # result check
        # repeat_times = self.result_dic.get ('repeat_times', 1)
        repeat_times = 10
        topic = self.result_dic.get ('topic', 'se_voice')
        result_msg = self.result_dic.get ('result_msg', None)

        key_words = [result_msg, f'"projectType":{self.project_id}']
        test_result = {}
        for index in range (repeat_times):
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=60)
            my_log.info (f'result:{result}')
            if result:
                result = eval (result)
                score = result.get ('serialScore', 0)
                score = int (score)
                self.test_result = 'PASS'
                serialNum1 = result.get ('serialNum1', 0)
                test_result.update ({f'{serialNum1}': score})
            else:
                self.test_result = 'FAIL'

        my_log.info (f'test_result:{test_result}')
        # my_log.info (f'expect_core:{expect_core}')

        file_dict = {f'{file_name}': test_result}
        my_log.info (f'file_dict:{file_dict}')

        target_dict = {}
        if os.path.exists (result_file):
            target_dict = readFile.read_yaml_dict (result_file)

        if target_dict:
            target_dict.update (file_dict)
        else:
            target_dict = file_dict
        ret = readFile.dump_file (result_file, target_dict)

        return

    def run_one_dir(self, dir_name, file_list):
        # keep result
        result_file = os.path.join (LOG_DIR, 'rope_skip.yaml')

        for file_name in file_list:
            file_name = os.path.join (self.video_path_dir, dir_name, file_name)
            self.run_one_file(self.project_id, file_name)
        return

    def run_one_loop(self):
        obj_list = os.listdir (self.video_path_dir)
        for obj in obj_list:
            path = os.path.join (self.video_path_dir, obj)
            my_log.info(f'path:{path}')
            if os.path.isfile(path) and '.mp4' in obj:
                self.run_one_file (path)
            elif os.path.isdir(path):
                file_list = os.listdir (path)
                self.run_one_dir(obj, file_list)

        return

    def test_run(self, open_dict, result_dic):
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        project_id = self.ai_sport.config(project_name=self.project_name)
        self.project_id = project_id
        self.locationId = open_dict.get ('locationId', None)
        self.open_dict = open_dict
        self.result_dic = result_dic

        self.test_result = 'FAIL'
        self.test_mode = 'free_mode'
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.run_one_loop ()
        else:
            retry = 2
        for index in range(retry):
            self.run_one_loop()
            if self.test_result == 'PASS':
                break

        return

    def tearDown(self) -> None:
        # close free mode must
        file = None
        if self.test_mode == 'free_mode':
            file = os.path.join (COMMON_DIR, 'CloseProjFreeMode.yaml')
        else:
            file = os.path.join (COMMON_DIR, 'CloseProjItemizedTest.yaml')

        close_dict = readFile.read_yaml_dict (file)
        close_dict.update ({"locationId": self.locationId})
        close_dict.update ({"projectType": self.project_id})
        self.ai_sport.close_proj_by_dict (close_dict)

        if self.ffmpeg:
            self.ffmpeg.stop()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1, is_free_mode=True)
        # 退出AI智慧平台
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass
