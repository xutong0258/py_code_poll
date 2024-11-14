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



class Push_M_Dir_Video_Sync():

    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        if ENV == 'Linux':
            self.video_path_dir_1 = cfg_dict['video_path_dir_linux_1']
            self.video_path_dir_2 = cfg_dict['video_path_dir_linux_2']
        else:
            self.video_path_dir_1 = cfg_dict['video_path_dir_win_1']
            self.video_path_dir_2 = cfg_dict['video_path_dir_win_2']

        self.whole_rtsp_1 = cfg_dict.get('rtsp_url_1', None)
        self.whole_rtsp_2 = cfg_dict.get ('rtsp_url_2', None)
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)
        
        # self.ai_sport.reset_kafka_to_lastest()

        self.test_result = 'FAIL'
        self.mysql.update_sql(sql_list)
        return

    def send_location_msg(self):
        student_num = self.mysql.get_student_num ()
        file = os.path.join(self.path_dir, 'locationId.yaml')
        if os.path.exists(file):
            if self.task_content_id_list:
                index = 0
                for item in self.task_content_id_list:
                    apend_dic = {'audioPlaying': 0,
                                 "taskContentId": item,
                                 "locationId": self.locationId_list[index],}
                    self.ai_sport.send_msg_by_yaml_file (file, apend_dic=apend_dic)
                    index = index + 1
            else:
                apend_dic = {'audioPlaying': 0,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file (file, apend_dic=apend_dic)
        return

    def run_one_loop(self):
        total_list_1 = list()
        for item in self.video_path_dir_1:
            if ENV == 'Linux':
                pass
            else:
                item = eval(item)
            files = os.listdir(item)
            for index in files:
                file = os.path.join(item, index)
                total_list_1.append(file)

        total_list_2 = list()
        for item in self.video_path_dir_2:
            if ENV == 'Linux':
                pass
            else:
                item = eval(item)
            files = os.listdir(item)
            for index in files:
                file = os.path.join(item, index)
                total_list_2.append(file)

        index = 0
        for file_name in total_list_1:
            self.mysql.set_test_project_db (proj_name=self.project_name, is_disabled=0, is_free_mode=True)
            if '.mp4' not in file_name:
                continue
            print(f'file_name:{file_name}')
            my_log.info(f'file_name:{file_name}')
            is_loop = self.result_dic.get ('is_loop', True)
            self.ffmpeg_1 = start_fake_camera_simple(file_name, whole_rtsp=self.whole_rtsp_1, is_loop=is_loop)
            self.ffmpeg_2 = start_fake_camera_simple (total_list_2[index], whole_rtsp=self.whole_rtsp_2, is_loop=is_loop)
            index = index + 1

            # send locationId
            self.send_location_msg()
            # self.ai_sport.reset_kafka_to_lastest()

            topic =  self.result_dic.get ('topic', 'se_voice')
            result_msg = self.result_dic.get ('result_msg', None)
            timeout = self.result_dic.get ('timeout', 30)

            if result_msg:
                # result check
                key_words = [result_msg, f'"projectType":{self.project_id}']
                key_words = [result_msg]
                result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int(timeout))
                my_log.info (f'result:{result}')
                if result:
                    self.test_result = 'FAIL'
                else:
                    self.test_result = 'PASS'

                self.test_mode = self.result_dic.get ('test_mode', None)
                dict_para = {
                    'project_name': self.project_name,
                    'test_name': file_name,
                    'test_result': self.test_result,
                    'test_mode': self.test_mode
                }
                readFile.update_result(LOG_DIR, dict_para)
        return

    def test_run(self, open_dict_list=None, result_dic=None):
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
        self.result_dic = result_dic
        self.test_mode = self.result_dic.get ('test_mode', None)

        self.task_content_id_list = list ()
        self.locationId_list = list ()

        for open_dict in open_dict_list:
            locationId = open_dict.get ('locationId', None)

            # close free mode must
            self.ai_sport.close_free_mode (locationId, project_id)
            self.locationId_list.append (locationId)

            # send openProjFreeMode
            task_content_id = self.ai_sport.open_proj_by_dict (open_dict)
            self.task_content_id_list.append (task_content_id)

        self.ffmpeg_1 = None

        while True:
            self.run_one_loop()
            time.sleep(3)

        return

    def tearDown(self) -> None:
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1, is_free_mode=True)
        # 退出AI智慧平台
        self.ai_sport.logout(self.project_id, self.test_mode)
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass