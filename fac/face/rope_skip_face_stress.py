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
        self.rtsp_url_1 = cfg_dict.get ('rtsp_url_1', None)
        self.rtsp_url_2 = cfg_dict.get ('rtsp_url_2', None)

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

        # self.ai_sport.reset_kafka_to_lastest()
        self.mysql.update_sql(sql_list)
        return

    def send_rope_skip_msg(self, project_id, task_content_id, locationId, result_dic):
        # send messageComment_startOff
        file = os.path.join(self.path_dir, 'messageComment_startOff.yaml')
        apend_dic = {"locationId": locationId,
                    "taskContentId": task_content_id,
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


        # 断言 "messageComment":"TimeStartToRunAnswer"
        topic = 'se_notify'
        key_words = ['"messageComment":"TimeStartToRunAnswer"', f'"projectType":{project_id}']
        result = self.ai_sport.get_kafka_message(key_words=key_words, topic=topic, timeout=3)
        # self.assertIsNotNone(result, "result is OK")
        my_log.info(f'score_voice:{result}')

        return

    def run_one_dir(self, project_id, result_dic, dir_name, file_list):
        # keep result
        result_file = os.path.join (LOG_DIR, 'rope_skip.yaml')

        for file_name in file_list:
            self.ai_sport.reset_kafka_to_lastest ()

            file_name = os.path.join (self.video_path_dir, dir_name, file_name)

            if ENV == 'Linux':
                pass
            else:
                file_name = file_name.replace ('/', '\\')

            # push video
            my_log.info ("开始推送视频")
            self.ffmpeg_1 = start_fake_camera_simple (self.video_path_1, whole_rtsp=self.rtsp_url_1)
            self.ffmpeg_2 = start_fake_camera_simple (self.video_path_1, whole_rtsp=self.rtsp_url_2)

            # 断言 se_voice "audioType":"ready"
            topic = 'se_voice'
            key_words = ['"audioType":"ready"', f'"projectType":{project_id}']
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=20)
            # self.assertIsNotNone(result, "result is OK")
            my_log.info (f'score_voice:{result}')

            # self.ffmpeg.stop ()
            # push video
            my_log.info ("开始推送视频")
            # self.ffmpeg = start_fake_camera_simple (self.video_path_2, is_loop=False, whole_rtsp=self.whole_rtsp)
            self.ffmpeg_1 = start_fake_camera_simple (file_name, is_loop=False, whole_rtsp=self.rtsp_url_1)
            self.ffmpeg_2 = start_fake_camera_simple (file_name, is_loop=False, whole_rtsp=self.rtsp_url_2)

            index = 0
            for task_content_id in self.task_content_id_list:
                self.send_rope_skip_msg(project_id, task_content_id, self.locationId_list[index], result_dic)
                index = index + 1

            topic = result_dic.get ('topic', 'se_voice')
            result_msg = result_dic.get ('result_msg', None)
            timeout = result_dic.get ('timeout', 70)

            if result_msg:
                # result check
                key_words = [result_msg, f'"projectType":{project_id}']
                key_words = [result_msg]
                result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int(timeout))
                my_log.info (f'result:{result}')
                if result:
                    self.test_result = 'FAIL'
                else:
                    self.test_result = 'PASS'

                self.test_mode = result_dic.get ('test_mode', None)
                dict_para = {
                    'project_name': self.project_name,
                    'test_name': file_name,
                    'test_result': self.test_result,
                    'test_mode': self.test_mode
                }
                readFile.update_result(LOG_DIR, dict_para)


        return

    def run_one_loop(self, project_id, result_dic=None):
        dirs_list = os.listdir (self.video_path_dir)
        for dir_name in dirs_list:
            path = os.path.join (self.video_path_dir, dir_name)
            my_log.info(f'path:{path}')
            if not os.path.isdir(path):
                continue
            file_list = os.listdir (path)

            self.run_one_dir(project_id, result_dic, dir_name, file_list)

        return
    def test_run(self, result_dic=None, open_dict_list=None):
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

        task_content_id = None
        self.task_content_id_list = list()
        self.locationId_list = list()

        # close free mode must
        for open_dict in open_dict_list:
            locationId = open_dict.get ('locationId', None)
            self.ai_sport.close_free_mode(locationId, project_id)
            self.locationId_list.append (locationId)

            # send openProjFreeMode
            task_content_id = self.ai_sport.open_proj_by_dict (open_dict)
            self.task_content_id_list.append (task_content_id)

        self.test_result = 'FAIL'
        self.test_mode = 'face_mode'
        self.ffmpeg_1 = None
        self.ffmpeg_2 = None

        while True:
            self.run_one_loop (project_id, result_dic)

        return

    def tearDown(self) -> None:
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()

        if self.ffmpeg_2:
            self.ffmpeg_2.stop()

        # 退出AI智慧平台
        # self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1)
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass