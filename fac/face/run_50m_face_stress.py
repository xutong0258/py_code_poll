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
    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.rtsp_url_1 = cfg_dict.get ('rtsp_url_1', None)
        self.rtsp_url_2 = cfg_dict.get ('rtsp_url_2', None)

        self.ffmpeg_2 = None
        self.test_result = 'FAIL'

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
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0)
        self.ai_sport.reset_kafka_to_lastest()

        # send start video
        # self.ffmpeg_1 = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.rtsp_url_1)
        self.mysql.update_sql(sql_list)
        return


    def send_run_msg(self, size_m):
        if size_m < 25:
            time.sleep(9)
        else:
            time.sleep (13)

        # assert faceAutoRecResult
        topic = 'se_notify'
        key_words = ['faceAutoRecResult', f'"projectType":{self.project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=4)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')


        # messageComment_ready
        file = os.path.join(self.path_dir, 'messageComment_ready.yaml')
        self.ai_sport.send_msg_by_yaml_file(file, self.task_content_id)

        # 断言
        topic = 'se_voice'
        key_words = ['"audioType":"ready"', f'"projectType":{self.project_id}']
        result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=1)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info (f'score_voice:{result}')


        # startOff
        file = os.path.join(self.path_dir, 'messageComment_startOff.yaml')
        self.ai_sport.send_msg_by_yaml_file(file, self.task_content_id)

        # 断言
        topic = 'se_voice'
        key_words = ['"audioType":"start"', f'"projectType":{self.project_id}']
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

        topic = self.result_dic.get ('topic', 'se_voice')
        result_msg = self.result_dic.get ('result_msg', None)

        if result_msg:
            # 断言 播报成绩：score语音
            key_words = result_msg
            result = self.ai_sport.get_kafka_message_or(key_words=key_words, topic=topic, timeout=int(size_m), project_id=self.project_id)
            self.test_result = 'FAIL'
            if result:
                self.test_result = 'PASS'
            else:
                self.test_result = 'FAIL'

        return

    def run_one_file(self, file_name):
        if '.mp4' not in file_name:
            return
        if ENV == 'Linux':
            pass
        else:
            file_name = file_name.replace ('/', '\\')

        is_loop = self.result_dic.get ('is_loop', True)
        my_log.info (f'file_name:{file_name}')

        self.ffmpeg_1 = start_fake_camera_simple (file_name, whole_rtsp=self.rtsp_url_1, is_loop=True)
        self.ffmpeg_2 = start_fake_camera_simple (file_name, whole_rtsp=self.rtsp_url_2, is_loop=True)
        self.ai_sport.reset_kafka_to_lastest ()

        size = os.path.getsize (file_name)
        # print (f"File size: {size} bytes")

        size_m = size / (1024 * 1024)
        size_m = int (size_m)
        # print (f"File size: {size_m} Mbytes")

        self.send_run_msg (size_m=size_m)
        return

    def run_one_dir(self, dir_name, file_list):
        for file_name in file_list:
            self.mysql.set_test_project_db (proj_name=self.project_name, is_disabled=0, is_free_mode=True)
            if '.mp4' not in file_name:
                continue
            file_name = os.path.join (self.video_path_dir, dir_name, file_name)
            self.run_one_file(file_name)
        return

    def run_one_loop(self):
        total_list = os.listdir (self.video_path_dir)
        for item in total_list:
            obj_name = os.path.join (self.video_path_dir, item)
            if os.path.isdir (obj_name):
                file_list = os.listdir (obj_name)
                self.run_one_dir (item, file_list)
            else:
                self.run_one_file (obj_name)
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
        self.task_content_id = self.ai_sport.open_proj_by_dict(open_dict, need_wait=False)

        self.ffmpeg_1 = None
        self.ffmpeg_2 = None
        self.test_result = 'FAIL'
        self.test_mode = 'face_mode'
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.run_one_loop()
        else:
            retry = 2
        for index in range(retry):
            self.run_one_loop()
            if TEST_MODE == 'STRESS_TEST':
                time.sleep(30)
            elif self.test_result == 'PASS':
                break

        return

    def tearDown(self) -> None:
        file = None
        if self.test_mode == 'free_mode':
            file = os.path.join(COMMON_DIR, 'CloseProjFreeMode.yaml')
        else:
            file = os.path.join(COMMON_DIR, 'CloseProjItemizedTest.yaml')

        close_dict = readFile.read_yaml_dict(file)
        close_dict.update({"locationId": self.locationId})
        close_dict.update ({"projectType": self.project_id})
        self.ai_sport.close_proj_by_dict(close_dict)
        
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
