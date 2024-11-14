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

        self.video_path_3 = cfg_dict.get('video_path_3', None)
        if self.video_path_3:
            self.video_path_3 = eval(self.video_path_3)
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
            self.ai_sport.reset_kafka_to_lastest()
        self.test_result = 'FAIL'
        self.mysql.update_sql(sql_list)
        return


    def push_video(self):
        # push video
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        if self.ffmpeg_2:
            self.ffmpeg_2.stop()
        if self.ffmpeg_3:
            self.ffmpeg_3.stop()

        self.ffmpeg_1 = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.rtsp_url_1)
        self.ffmpeg_2 = start_fake_camera_simple(self.video_path_2, whole_rtsp=self.rtsp_url_2)
        if self.video_path_3:
            self.ffmpeg_3 = start_fake_camera_simple(self.video_path_3, whole_rtsp=self.rtsp_url_3)

        return

    def run_one_loop(self, project_id, open_dict, result_dic, task_content_id):
        # push video
        self.push_video ()

        if not self.open_once:
            # close free mode must
            self.test_mode = result_dic.get ('test_mode', 'face_mode')
            self.locationId = open_dict.get ('locationId', None)
            self.ai_sport.close_free_mode (self.locationId, project_id)

            # open
            task_content_id = self.ai_sport.open_proj_by_dict (open_dict, need_wait=True)

        # 断言 "messageComment":"faceAutoRecResult"
        topic = 'se_notify'
        key_words = ['"messageComment":"faceAutoRecResult"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message(key_words=key_words,  topic=topic, timeout=10)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info(f'score_voice:{result}')


        # send ready
        file = os.path.join(self.path_dir, '0_ready.yaml')
        apend_dic = {'taskContentId': task_content_id,
                     'truthTaskContentId': task_content_id,
                    }
        self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

        # assert
        topic = 'se_voice'
        key_words = ['"audioType":"ready"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=6)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info(f'score_voice:{result}')

        # start off
        file = os.path.join(self.path_dir, '1_startOff.yaml')
        apend_dic = {'taskContentId': task_content_id,
                     'truthTaskContentId': task_content_id,
                    }
        self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

        # assert
        topic = 'se_voice'
        key_words = ['"audioType":"start"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=6)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info(f'score_voice:{result}')

        # TimeStartToRun
        time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d%H:%M:%S")
        file = os.path.join(self.path_dir, 'TimeStartToRun.yaml')
        apend_dic = {
                     'taskContentId': task_content_id,
                     'truthTaskContentId': task_content_id,
                     'pengTimeText': f'{time_stamp}',
                     }
        self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)


        topic = result_dic.get ('topic', 'se_notify')
        timeout = result_dic.get ('timeout', 120)
        result_msg = result_dic.get ('result_msg', None)

        if result_msg:
            # key_words = result_msg
            # result = self.ai_sport.get_kafka_message_or(key_words=key_words, topic=topic, timeout=int(timeout), project_id=project_id)
            key_words = [result_msg, f'"projectType":{project_id}']
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int (timeout))
            my_log.info(f'score_voice:{result}')
            if result:
                self.test_result = 'PASS'
            else:
                self.test_result = 'FAIL'

            self.test_mode = result_dic.get ('test_mode', 'face_mode')
            dict_para = {
                'project_name': self.project_name,
                'test_name': self.test_name,
                'test_result': self.test_result,
                'test_mode': f'{self.test_mode}'
            }

            readFile.update_result(LOG_DIR, dict_para)
        return

    def test_run(self, open_dict, result_dic=None):
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        project_id = self.ai_sport.config(project_name=self.project_name)
        self.project_id = project_id

        self.open_once = result_dic.get ('open_once', True)
        task_content_id = None
        if self.open_once:
            # close free mode must
            self.test_mode = result_dic.get ('test_mode', 'face_mode')
            self.locationId = open_dict.get ('locationId', None)
            self.ai_sport.close_free_mode (self.locationId, project_id)

            # open
            task_content_id = self.ai_sport.open_proj_by_dict (open_dict, need_wait=True)

        self.ffmpeg_1 = None
        self.ffmpeg_2 = None
        self.ffmpeg_3 = None
        self.test_result = 'FAIL'
        self.test_mode = 'face_mode'
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.run_one_loop (project_id, open_dict, result_dic, task_content_id)
                time.sleep(5)
        else:
            retry = 2
        for index in range(retry):
            self.run_one_loop(project_id, open_dict, result_dic, task_content_id)
            time.sleep(5)
            if self.test_result == 'PASS':
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
        self.ai_sport.close_free_mode(self.locationId, self.project_id)

        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        if self.ffmpeg_2:
            self.ffmpeg_2.stop()
        if self.ffmpeg_3:
            self.ffmpeg_3.stop()

        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1)
        # 第十八步：退出AI智能体育项目
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass
