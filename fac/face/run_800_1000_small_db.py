# coding=utf-8

import os
import sys
import json
import time
import unittest
import warnings
import platform
from pathlib import Path


file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)
base_name = os.path.basename(path_dir)

while 'se-autotest' not in base_name:
    path_dir = os.path.dirname(path_dir)
    base_name = os.path.basename(path_dir)

sys.path.append(path_dir)

from common.rtsp import *

from util import *
import readFile

from common.mylogger import my_log
from component.ai_sport import *
from component.mysql import Mysql
from common.contants import *



class Run800M_Common():
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

        if ENV == 'Linux':
            self.video_path_dir = cfg_dict['video_path_dir_linux']
        else:
            self.video_path_dir = eval(cfg_dict['video_path_dir_win'])

        self.rtsp_url_3 = cfg_dict.get('rtsp_url_3', None)

        self.video_path_4 = cfg_dict.get ('video_path_4', None)
        if self.video_path_4:
            self.video_path_4 = eval(self.video_path_4)
            self.rtsp_url_4 = cfg_dict.get('rtsp_url_4', None)


        return

    def setUp(self, sql_list) -> None:
        warnings.simplefilter('ignore', ResourceWarning)
        my_log.info(f"================{__file__} 测试开始 ===================")
        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0)

        if TEST_MODE != 'STRESS_TEST':
            # self.ai_sport.reset_kafka_to_lastest()
            pass
        self.test_result = 'FAIL'
        self.mysql.update_sql(sql_list)
        return


    def push_video(self, file_name):
        # push video
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        if self.ffmpeg_3:
            self.ffmpeg_3.stop()
        if self.ffmpeg_4:
            self.ffmpeg_4.stop()

        self.ffmpeg_3 = start_fake_camera_simple (file_name, whole_rtsp=self.rtsp_url_3)
        self.ffmpeg_1 = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.rtsp_url_1)
        self.ffmpeg_4 = start_fake_camera_simple(self.video_path_4, whole_rtsp=self.rtsp_url_4)

        return

    def run_one_dir(self, dir_name, file_list):
        for file_name in file_list:
            if 'son' in file_name or 'start' in file_name:
                continue
            self.ai_sport.reset_kafka_to_lastest ()
            self.ai_sport.close_free_mode (self.locationId, self.project_id)
            topic = 'se_notify'
            key_words = ['"messageComment":"CloseProjAnswer"']
            timeout = 60
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=timeout)

            # wait last close then open
            task_content_id = self.ai_sport.open_proj_by_dict (self.open_dict, need_wait=False)
            topic = 'se_notify'
            key_words = ['"messageComment":"OpenProjAnswer"']
            timeout = 60
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=timeout)

            file_name = os.path.join (self.video_path_dir, dir_name, file_name)
            if ENV == 'Linux':
                pass
            else:
                file_name = file_name.replace ('/', '\\')

            self.push_video(file_name)

            # send ready
            file = os.path.join (self.path_dir, '0_ready.yaml')
            apend_dic = {'taskContentId': task_content_id,
                         'truthTaskContentId': task_content_id,
                         }
            self.ai_sport.send_msg_by_yaml_file (file, apend_dic=apend_dic)

            # must assert
            topic = 'se_voice'
            key_words = ['"audioType":"ready"', f'"projectType":{self.project_id}']
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=5)
            # self.assertIsNotNone(result, "result is OK")
            my_log.info (f'score_voice:{result}')

            # start off
            file = os.path.join (self.path_dir, '1_startOff.yaml')
            apend_dic = {'taskContentId': task_content_id,
                         'truthTaskContentId': task_content_id,
                         }
            self.ai_sport.send_msg_by_yaml_file (file, apend_dic=apend_dic)

            # must assert
            topic = 'se_voice'
            key_words = ['"audioType":"start"', f'"projectType":{self.project_id}']
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=5)
            # self.assertIsNotNone(result, "result is OK")
            my_log.info (f'score_voice:{result}')

            # TimeStartToRun
            time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d%H:%M:%S")
            file = os.path.join (self.path_dir, 'TimeStartToRun.yaml')
            apend_dic = {
                'taskContentId': task_content_id,
                'truthTaskContentId': task_content_id,
                'pengTimeText': f'{time_stamp}',
            }
            self.ai_sport.send_msg_by_yaml_file (file, apend_dic=apend_dic)

            topic = self.result_dic.get ('topic', 'se_notify')
            timeout = self.result_dic.get ('timeout', 120)
            result_msg = self.result_dic.get ('result_msg', None)

            if result_msg:
                key_words = [result_msg, f'"projectType":{self.project_id}']
                # 断言score语音
                result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int (timeout))
                # self.assertIsNotNone(result, "result is OK")
                my_log.info (f'score_voice:{result}')
                if result:
                    self.test_result = 'PASS'
                else:
                    self.test_result = 'FAIL'

                self.test_mode = self.result_dic.get ('test_mode', 'face_mode')
                dict_para = {
                    'project_name': self.project_name,
                    'test_name': self.test_name,
                    'test_result': self.test_result,
                    'test_mode': f'{self.test_mode}'
                }

                readFile.update_result (LOG_DIR, dict_para)

            # for score out
            time.sleep(60*2)
        return

    def run_one_loop(self):
        dirs_list = os.listdir (self.video_path_dir)


        for dir_name in dirs_list:
            class_id = os.path.basename(dir_name)
            cfg_file = os.path.join (self.path_dir, f'OpenProj_{dir_name}.yaml')
            open_dict = readFile.read_yaml_dict (cfg_file)
            open_dict_str = str (open_dict)
            open_dict_str = open_dict_str.replace ('rtsp_url_1', f'{self.rtsp_url_1}')
            open_dict_str = open_dict_str.replace ('rtsp_url_2', f'{self.rtsp_url_2}')
            open_dict_str = open_dict_str.replace ('rtsp_url_3', f'{self.rtsp_url_3}')
            open_dict_str = open_dict_str.replace ('rtsp_url_4', f'{self.rtsp_url_4}')
            open_dict = eval (open_dict_str)
            self.open_dict = open_dict

            self.locationId = open_dict.get ('locationId', None)
            # self.ai_sport.close_free_mode (self.locationId, self.project_id)
            # wait last close then open
            # self.task_content_id = self.ai_sport.open_proj_by_dict (open_dict, need_wait=True)

            path = os.path.join (self.video_path_dir, dir_name)
            my_log.info(f'path:{path}')
            if not os.path.isdir(path):
                continue
            file_list = os.listdir (path)

            self.run_one_dir(dir_name, file_list)

        return

    def test_run(self, result_dic=None):
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        self.project_id = self.ai_sport.config(project_name=self.project_name)
        self.result_dic = result_dic

        task_content_id = None
        # close free mode must
        self.test_mode = result_dic.get ('test_mode', 'face_mode')


        self.ffmpeg_1 = None
        self.ffmpeg_3 = None
        self.ffmpeg_4 = None
        self.test_result = 'FAIL'
        self.test_mode = 'face_mode'
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.run_one_loop ()
                time.sleep(15)
        else:
            retry = 2
        for index in range(retry):
            self.run_one_loop()
            time.sleep(20)
            if self.test_result == 'PASS':
                break

        return

    def tearDown(self) -> None:
        # close free mode must
        self.ai_sport.close_free_mode (self.locationId, self.project_id)

        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        if self.ffmpeg_3:
            self.ffmpeg_3.stop()
        if self.ffmpeg_4:
            self.ffmpeg_4.stop()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1)
        # 第十八步：退出AI智能体育项目
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass
