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
class Face_Stress_Common():
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
            self.whole_rtsp_2 = cfg_dict.get ('rtsp_url_2', None)
        self.whole_rtsp_1 = cfg_dict.get('rtsp_url_1', None)
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

    def run_one_loop(self, result_dic, project_id):
        """
        自由模式项目开启
        """
        # push video
        # my_log.info("开始推送视频")
        # self.ffmpeg = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.whole_rtsp)
        # self.ai_sport.reset_kafka_to_lastest ()

        for task_content_id in self.task_content_id_list:
            # send audioMsgType_java
            if current_enable:
                file = os.path.join(self.cfg_dir, 'audioMsgType_java.yaml')
                apend_dic = {'audioPlaying': 1,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

                # send audioMsgType_java
                file = os.path.join(self.cfg_dir, 'audioMsgType_java.yaml')
                apend_dic = {'audioPlaying': 0,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

            # "audioType":"watchCamera""
            topic = 'se_voice'
            key_words = ['"messageComment":"faceAutoRecResult"', f'"projectType":{project_id}']
            result = self.ai_sport.get_kafka_message(key_words=key_words,  topic=topic, timeout=1)

            has_watchCamera_msg = result_dic.get('has_watchCamera_msg', None)
            if current_enable:
                # send audioMsgType_watchCamera
                file = os.path.join(self.cfg_dir, 'audioMsgType_watchCamera.yaml')
                apend_dic = {'audioPlaying': 1,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

                # send audioMsgType_watchCamera
                file = os.path.join(self.cfg_dir, 'audioMsgType_watchCamera.yaml')
                apend_dic = {'audioPlaying': 0,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

            if current_enable:
                # send locationId
                student_num = self.mysql.get_student_num ()
                file = os.path.join (self.cfg_dir, 'locationId.yaml')
                apend_dic = {'audioPlaying': 0,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file (file, taskContentId=task_content_id)

            if current_enable:
                # send audioMsgType_java
                file = os.path.join(self.cfg_dir, 'audioMsgType_java.yaml')
                apend_dic = {'audioPlaying': 1,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

                # send audioMsgType_java
                file = os.path.join(self.cfg_dir, 'audioMsgType_java.yaml')
                apend_dic = {'audioPlaying': 0,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

            has_start_msg = result_dic.get('has_start_msg', None)
            if current_enable:
                # send audioMsgType_start
                file = os.path.join(self.cfg_dir, 'audioMsgType_start.yaml')
                apend_dic = {'audioPlaying': 1,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

                # send audioMsgType_start
                file = os.path.join(self.cfg_dir, 'audioMsgType_start.yaml')
                apend_dic = {'audioPlaying': 0,
                             "taskContentId": task_content_id}
                self.ai_sport.send_msg_by_yaml_file(file, apend_dic=apend_dic)

        return

    def test_run(self, result_dic=None, open_dict_list=None):
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

        task_content_id = None
        self.task_content_id_list = list()
        self.locationId_list = list()
        # close free mode must
        if open_dict_list:
            for open_dict in open_dict_list:
                locationId = open_dict.get ('locationId', None)
                self.ai_sport.close_free_mode(locationId, self.project_id)
                self.locationId_list.append(locationId)

                # send openProjFreeMode
                task_content_id = self.ai_sport.open_proj_by_dict (open_dict)
                self.task_content_id_list.append(task_content_id)
        else:
            # close
            self.locationId = open_dict.get ('locationId', None)
            self.ai_sport.close_free_mode (self.locationId, self.project_id)

            # send OpenProj
            self.locationId = open_dict.get('locationId', None)
            task_content_id = self.ai_sport.open_proj_by_dict(open_dict)

        self.ffmpeg_1 = start_fake_camera_simple(self.video_path_1, whole_rtsp=self.whole_rtsp_1)

        if self.video_path_2:
            self.ffmpeg_2 = start_fake_camera_simple (self.video_path_2, whole_rtsp=self.whole_rtsp_2)

        self.test_mode = 'face_mode'
        while True:
            self.run_one_loop(result_dic, project_id)

        return


    def tearDown(self) -> None:
        # 退出AI智慧平台
        if self.ffmpeg_1:
            self.ffmpeg_1.stop()

        if self.ffmpeg_2:
            self.ffmpeg_2.stop()

        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=1)
        self.ai_sport.logout(self.project_id, self.test_mode)

        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass
