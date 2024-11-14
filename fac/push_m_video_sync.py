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



class Push_M_Video_Sync():
    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = eval(cfg_dict['video_path_1'])
        self.rtsp_url_1 = cfg_dict['rtsp_url_1']

        self.video_path_2 = eval(cfg_dict['video_path_2'])
        self.rtsp_url_2 = cfg_dict['rtsp_url_2']

        self.video_path_3 = cfg_dict.get('video_path_3', None)
        if self.video_path_3:
            self.video_path_3 = eval(self.video_path_3)
            self.rtsp_url_3 = cfg_dict['rtsp_url_3']

        self.video_path_4 = cfg_dict.get('video_path_4', None)
        if self.video_path_4:
            self.video_path_4 = eval(self.video_path_4)
            self.rtsp_url_4 = cfg_dict['rtsp_url_4']

        self.video_path_5 = cfg_dict.get('video_path_5', None)
        if self.video_path_5:
            self.video_path_5 = eval(self.video_path_5)
            self.rtsp_url_5 = cfg_dict['rtsp_url_5']

        self.video_path_6 = cfg_dict.get('video_path_6', None)
        if self.video_path_6:
            self.video_path_6 = eval(self.video_path_6)
            self.rtsp_url_6 = cfg_dict['rtsp_url_6']
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)

        self.ai_sport.reset_kafka_to_lastest()

        self.mysql.update_sql(sql_list)

        self.test_mode = None
        self.ffmpeg_1 = None
        self.ffmpeg_2 = None
        self.ffmpeg_3 = None
        return


    def run_one_loop(self, open_dict, result_dic, project_id):
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        project_id = self.ai_sport.config(project_name=self.project_name)

        self.multipleLocationIds = open_dict.get ('multipleLocationIds', None)

        # close free mode must
        file = None
        if self.test_mode == 'free_mode':
            file = os.path.join(COMMON_DIR, 'CloseProjFreeMode.yaml')
        else:
            file = os.path.join(COMMON_DIR, 'CloseProjItemizedTest.yaml')

        close_dict = readFile.read_yaml_dict(file)
        close_dict.update({"locationId": self.locationId})
        close_dict.update ({"projectType": self.project_id})
        if self.multipleLocationIds:
            close_dict.update ({"multipleLocationIds": self.multipleLocationIds})
        self.ai_sport.close_proj_by_dict(close_dict)

        # send OpenProj
        self.test_mode = result_dic.get ('test_mode', 'free_mode')
        task_content_id = self.ai_sport.open_proj_by_dict(open_dict, self.test_mode)

        is_loop = result_dic.get ('is_loop', True)

        self.ffmpeg_1 = start_fake_camera_simple(self.video_path_1, is_loop=is_loop, whole_rtsp=self.rtsp_url_1)
        self.ffmpeg_2 = start_fake_camera_simple(self.video_path_2, is_loop=is_loop, whole_rtsp=self.rtsp_url_2)

        self.ffmpeg_3 = None
        if self.video_path_3:
            self.ffmpeg_3 = start_fake_camera_simple (self.video_path_3, is_loop=is_loop, whole_rtsp=self.rtsp_url_3)

        self.ffmpeg_4 = None
        if self.video_path_4:
            self.ffmpeg_4 = start_fake_camera_simple (self.video_path_4, is_loop=is_loop, whole_rtsp=self.rtsp_url_4)

        self.ffmpeg_5 = None
        if self.video_path_5:
            self.ffmpeg_5 = start_fake_camera_simple (self.video_path_5, is_loop=is_loop, whole_rtsp=self.rtsp_url_5)

        self.ffmpeg_6 = None
        if self.video_path_6:
            self.ffmpeg_6 = start_fake_camera_simple (self.video_path_6, is_loop=is_loop, whole_rtsp=self.rtsp_url_6)

        topic = result_dic.get ('topic', 'se_voice')
        result_msg = result_dic.get ('result_msg', '"audioType":"score"')
        expect_core = result_dic.get ('expect_core')
        skip_assert = result_dic.get ('skip_assert', True)
        timeout = result_dic.get ('timeout', 20)

        # 断言score语音
        self.test_result = 'FAIL'
        key_words = result_msg
        result = self.ai_sport.get_kafka_message_or (key_words=key_words, topic=topic, timeout=int (timeout),
                                                     project_id=project_id
                                                     )
        my_log.info (f'score_voice:{result}')

        if result:
            self.test_result = 'PASS'
            acctual_result_dict = eval (result)
            serialScore = acctual_result_dict.get('serialScore', None)
            if serialScore:
                serialScore = round (serialScore, 2)
                my_log.info (f'serialScore:{serialScore}')
        else:
            self.test_result = 'FAIL'

        self.test_mode = result_dic.get ('test_mode', 'class_list')
        dict_para = {
            'project_name': self.project_name,
            'test_name': self.test_name,
            'test_result': self.test_result,
            'test_mode': f'{self.test_mode}'
        }

        readFile.update_result(LOG_DIR, dict_para)

        return

    def test_run(self, open_dict, result_dic):
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        project_id = self.ai_sport.config(project_name=self.project_name)
        self.project_id = project_id
        self.locationId = open_dict.get('locationId', None)

        self.ffmpeg_3 = None
        self.ffmpeg_4 = None
        self.ffmpeg_5 = None
        self.ffmpeg_6 = None
        my_log.info (f'TEST_MODE:{TEST_MODE}')
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.run_one_loop (open_dict, result_dic, project_id)
        else:
            max = 2
            for index in range(max):
                self.run_one_loop(open_dict, result_dic, project_id)
                if 'PASS' == self.test_result:
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
        if self.multipleLocationIds:
            close_dict.update ({"multipleLocationIds": self.multipleLocationIds})
        self.ai_sport.close_proj_by_dict(close_dict)

        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        if self.ffmpeg_2:
            self.ffmpeg_2.stop()
        if self.ffmpeg_3:
            self.ffmpeg_3.stop()
        if self.ffmpeg_4:
            self.ffmpeg_4.stop()
        if self.ffmpeg_5:
            self.ffmpeg_5.stop()
        if self.ffmpeg_6:
            self.ffmpeg_6.stop()

        # sun run keep project open for cpp reboot issue
        if '阳光跑' != self.project_name:
            self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1, is_free_mode=True)

        # 退出AI智慧平台
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass
