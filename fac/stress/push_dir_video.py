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



# unittest.TestCase
class Push_Dir_Video():
    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = cfg_dict.get('video_path_1', None)
        if self.video_path_1:
            self.video_path_1 = eval(cfg_dict['video_path_1'])

        if ENV == 'Linux':
            self.video_path_dir = cfg_dict['video_path_dir_linux']
        else:
            self.video_path_dir = eval(cfg_dict['video_path_dir_win'])

        self.rtsp_url_1 = cfg_dict.get('rtsp_url_1', None)
        self.rtsp_url_2 = cfg_dict.get('rtsp_url_2', None)
        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)
        
        # self.ai_sport.reset_kafka_to_lastest()

        self.test_result = 'FAIL'
        my_log.info (f'sql_list:{sql_list}')
        self.mysql.update_sql(sql_list)
        return

    def send_location_msg(self):
        student_num = self.mysql.get_student_num ()
        file = os.path.join(self.path_dir, 'locationId.yaml')
        if os.path.exists(file):
            if self.task_content_id_list:
                index = 0
                for item in self.task_content_id_list:
                    apend_dic = {"taskContentId": item,
                                 "locationId": self.locationId_list[index],}
                    self.ai_sport.send_msg_by_yaml_file (file, apend_dic=apend_dic)
                    index = index + 1
            else:
                raise ValueError (f'Need locationId')
        return

    def run_one_file(self, project_id, file_name):
        if '.mp4' not in file_name:
            return
        if ENV == 'Linux':
            pass
        else:
            file_name = file_name.replace ('/', '\\')

        is_loop = self.result_dic.get ('is_loop', True)
        self.ffmpeg_1 = start_fake_camera_simple (file_name, whole_rtsp=self.rtsp_url_1, is_loop=is_loop)

        if self.rtsp_url_2:
            self.ffmpeg_2 = start_fake_camera_simple (file_name, whole_rtsp=self.rtsp_url_2, is_loop=is_loop)

        # send locationId
        self.send_location_msg ()
        # self.ai_sport.reset_kafka_to_lastest()

        topic = self.result_dic.get ('topic', 'se_voice')
        result_msg = self.result_dic.get ('result_msg', None)
        timeout = self.result_dic.get ('timeout', 30)

        if result_msg:
            # result check
            key_words = [result_msg, f'"projectType":{project_id}']
            key_words = [result_msg]
            result = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int (timeout))
            my_log.info (f'result:{result}')
        return

    def run_one_dir(self, project_id, dir_name, file_list):
        for file_name in file_list:
            self.mysql.set_test_project_db (proj_name=self.project_name, is_disabled=0, is_free_mode=True)
            if '.mp4' not in file_name:
                continue
            file_name = os.path.join (self.video_path_dir, dir_name, file_name)
            self.run_one_file(project_id, file_name)

        return

    def run_one_loop(self, project_id, open_dict_list):
        for open_dict in open_dict_list:
            locationId = open_dict.get ('locationId', None)

            # close free mode must
            self.ai_sport.close_free_mode (locationId, project_id)
            self.locationId_list.append (locationId)

            # send openProjFreeMode
            task_content_id = self.ai_sport.open_proj_by_dict (open_dict)
            self.task_content_id_list.append (task_content_id)

            total_list = os.listdir(self.video_path_dir)
            for item in total_list:
                obj_name = os.path.join (self.video_path_dir, item)
                if os.path.isdir(obj_name):
                    file_list = os.listdir (obj_name)
                    self.run_one_dir (project_id, item, file_list)
                else:
                    self.run_one_file(project_id, obj_name)
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

        self.task_content_id_list = list()
        self.locationId_list = list()

        self.ffmpeg_1 = None

        while True:
            self.run_one_loop(project_id, open_dict_list)
            time.sleep(3)

        return

    def tearDown(self) -> None:
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()
        # self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1, is_free_mode=True)
        # 退出AI智慧平台
        self.ai_sport.logout(self.project_id, self.test_mode)
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass