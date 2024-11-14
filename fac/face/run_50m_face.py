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



class Run_50m_Face_Common():
    def __init__(self, path_dir, is_foul=False):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = eval(cfg_dict['video_path_1'])
        self.video_path_2 = eval(cfg_dict['video_path_2'])

        self.rtsp_url_1 = cfg_dict.get ('rtsp_url_1', None)
        self.rtsp_url_2 = cfg_dict.get ('rtsp_url_2', None)

        self.is_foul = is_foul
        self.ffmpeg_2 = None
        self.test_result = 'FAIL'
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)
        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0)
        # self.ai_sport.reset_kafka_to_lastest()

        # send start video
        # self.ffmpeg_1 = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.rtsp_url_1)
        self.mysql.update_sql(sql_list)
        return

    def update_run_result(self, result_dic) -> None:

        self.test_mode = result_dic.get ('test_mode', 'face_mode')
        dict_para = {
            'project_name': self.project_name,
            'test_name': self.test_name,
            'test_result': self.test_result,
            'test_mode': f'{self.test_mode}'
        }

        readFile.update_result(LOG_DIR, dict_para)
        return

    def run_one_loop(self, project_id, task_content_id, result_dic,  pre_check=False):
        topic = result_dic.get ('topic', 'se_voice')
        result_msg = result_dic.get ('result_msg', None)
        timeout = result_dic.get ('timeout', 60)

        if pre_check:
            key_words = [result_msg, f'"projectType":{project_id}']
            result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=int(timeout))
            self.test_result = 'FAIL'
            if result:
                self.test_result = 'PASS'
            else:
                self.test_result = 'FAIL'
            self.update_run_result(result_dic)
            return

        # assert faceAutoRecResult
        topic = 'se_notify'
        key_words = ['faceAutoRecResult', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=4)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')


        # messageComment_ready
        file = os.path.join(self.path_dir, 'messageComment_ready.yaml')
        self.ai_sport.send_msg_by_yaml_file(file, task_content_id)

        # 断言
        topic = 'se_voice'
        key_words = ['"audioType":"ready"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=1)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')


        # startOff
        file = os.path.join(self.path_dir, 'messageComment_startOff.yaml')
        self.ai_sport.send_msg_by_yaml_file(file, task_content_id)

        # 断言
        topic = 'se_voice'
        key_words = ['"audioType":"start"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=1)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')


        # send messageComment_TimeStartToRun
        file = os.path.join(self.path_dir, 'messageComment_TimeStartToRun.yaml')
        current_time = int (time.time ())
        # "2024-10-11 11:21:56 615"
        time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H：%M：%S %MS")
        apend_dic = {'pengTime': current_time,
                     'pengTimeText': time_stamp}
        self.ai_sport.send_msg_by_yaml_file(file)


        if result_msg:
            key_words = result_msg
            result = self.ai_sport.get_kafka_message_or(key_words=key_words, topic=topic, timeout=int(timeout), project_id=project_id)
            # result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=int (timeout))
            my_log.info(f'result:{result}')
            if result:
                self.test_result = 'PASS'
            else:
                self.test_result = 'FAIL'

            self.update_run_result (result_dic)

        return

    def test_run(self, open_dict, result_dic, pre_check=False):
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        project_id = self.ai_sport.config(project_name=self.project_name)
        self.project_id = project_id

        # close project
        self.locationId = open_dict.get ('locationId', None)
        self.ai_sport.close_free_mode(self.locationId, project_id)

        # open
        self.locationId = open_dict.get ('locationId', None)
        task_content_id = self.ai_sport.open_proj_by_dict(open_dict)

        self.ffmpeg_1 = start_fake_camera_simple (self.video_path_1, whole_rtsp=self.rtsp_url_1)
        self.ffmpeg_2 = start_fake_camera_simple (self.video_path_2, whole_rtsp=self.rtsp_url_2)
        self.ai_sport.reset_kafka_to_lastest ()

        self.test_result = 'FAIL'
        self.test_mode = 'face_mode'
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.run_one_loop (project_id, task_content_id, result_dic, pre_check)
                time.sleep (10)
        else:
            retry = 2
        for index in range(retry):
            self.run_one_loop(project_id, task_content_id, result_dic, pre_check)
            if self.test_result == 'PASS':
                break
            else:
                time.sleep (10)

        return

    def tearDown(self) -> None:
        file = None
        if self.test_mode == 'free_mode':
            file = os.path.join (COMMON_DIR, 'CloseProjFreeMode.yaml')
        else:
            file = os.path.join (COMMON_DIR, 'CloseProjItemizedTest.yaml')

        close_dict = readFile.read_yaml_dict (file)
        close_dict.update ({"locationId": self.locationId})
        close_dict.update ({"projectType": self.project_id})
        self.ai_sport.close_proj_by_dict (close_dict)
        
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()

        if self.ffmpeg_2:
            self.ffmpeg_2.stop()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1)
        # 第十八步：退出AI智能体育项目
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")
        return

if __name__ == '__main__':
    unittest.main()