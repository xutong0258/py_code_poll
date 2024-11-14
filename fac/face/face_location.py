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



class Face_Location_Common():
    def __init__(self, path_dir, foul_case=False):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        if foul_case:
            self.cfg_dir = os.path.join(path_dir, '../yaml_cfg')
        else:
            self.cfg_dir = path_dir

        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = eval(cfg_dict['video_path_1'])
        self.video_path_2 = cfg_dict.get('video_path_2', None)
        if self.video_path_2:
            self.video_path_2 = eval(self.video_path_2)
        self.whole_rtsp = cfg_dict.get ('rtsp_url_1', None)
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)

        self.test_result = 'FAIL'
        self.mysql.update_sql(sql_list)
        self.ai_sport.reset_kafka_to_lastest()
        self.ffmpeg = None
        return

    def send_location_msg(self, task_content_id) -> None:
        student_num = self.mysql.get_student_num ()
        file = os.path.join(self.path_dir, 'locationId.yaml')
        if os.path.exists(file):
            apend_dic = {'audioPlaying': 0,
                         "taskContentId": task_content_id}
            self.ai_sport.send_msg_by_yaml_file (file, apend_dic=apend_dic)
        return

    def run_one_loop(self, project_id, task_content_id, result_dic):
        # send locationId
        self.send_location_msg(task_content_id)

        topic = result_dic.get ('topic', 'se_voice')
        result_msg = result_dic.get ('result_msg', None)
        expect_core = result_dic.get ('expect_core')
        skip_assert = result_dic.get ('skip_assert', True)
        timeout = result_dic.get('timeout', 60)
        reverse_flag = result_dic.get ('reverse_flag', False)

        if result_msg:
            # to do debug issue
            key_words = [result_msg, f'"projectType":{project_id}']
            key_words = [result_msg]
            # key_words = [result_msg]
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int(timeout))
            my_log.info (f'result:{result}')
            if reverse_flag:
                if result:
                    self.test_result = 'FAIL'
                else:
                    self.test_result = 'PASS'
            else:
                if result:
                    self.test_result = 'PASS'
                else:
                    self.test_result = 'FAIL'

        if result_msg:
            self.test_mode = result_dic.get('test_mode', 'class_list')
            dict_para = {
                'project_name': self.project_name,
                'test_name': self.test_name,
                'test_result': self.test_result,
                'test_mode': f'{self.test_mode}'
            }

            readFile.update_result(LOG_DIR, dict_para)

        return

    def test_run(self, open_dict, result_dic):
        """
        自由模式项目开启
        """
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        project_id = self.ai_sport.config(project_name=self.project_name)
        self.project_id = project_id
        self.multipleLocationIds = open_dict.get ('multipleLocationIds', None)


        # close free mode must
        self.test_mode = result_dic.get ('test_mode', None)
        self.locationId = open_dict.get ('locationId', None)
        file = None
        if self.test_mode == 'free_mode':
            file = os.path.join(COMMON_DIR, 'CloseProjFreeMode.yaml')
        else:
            file = os.path.join(COMMON_DIR, 'CloseProjItemizedTest.yaml')

        close_dict = readFile.read_yaml_dict(file)
        close_dict.update({"locationId": self.locationId})
        close_dict.update ({"projectType": self.project_id})
        # sit up
        if self.multipleLocationIds:
            close_dict.update ({"multipleLocationIds": self.multipleLocationIds})
        self.ai_sport.close_proj_by_dict(close_dict)


        # send OpenProj
        task_content_id = self.ai_sport.open_proj_by_dict(open_dict, self.test_mode)

        # push video
        my_log.info("开始推送视频")
        self.ffmpeg = start_fake_camera_simple (self.video_path_1, is_loop=True, whole_rtsp=self.whole_rtsp)


        self.test_result = 'FAIL'
        self.test_mode = 'face_mode'
        my_log.info (f'TEST_MODE:{TEST_MODE}')
        if TEST_MODE == 'STRESS_TEST':
            while True:
                self.run_one_loop (project_id, task_content_id, result_dic)
        else:
            retry = 2
        for index in range(retry):
            my_log.info(f'retry:{index}')
            self.run_one_loop (project_id, task_content_id, result_dic)
            if 'PASS' == self.test_result:
                break

        return


    def tearDown(self) -> None:
        # 退出AI智慧平台
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

        if self.ffmpeg:
            self.ffmpeg.stop()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1, is_free_mode=True)
        self.ai_sport.logout(self.project_id, self.test_mode)
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass
