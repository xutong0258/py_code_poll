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
class Sit_Up_Free_Dir():

    def __init__(self, path_dir):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir
        cfg_file = os.path.join(path_dir, 'case_dict.yaml')
        cfg_dict = readFile.read_yaml_dict(cfg_file)

        self.project_name = cfg_dict["projectName"]
        self.test_name = cfg_dict.get("testName", None)

        self.video_path_1 = cfg_dict.get('video_path_1')
        if self.video_path_1:
            self.video_path_1 = eval(self.video_path_1)
        self.whole_rtsp = cfg_dict.get ('rtsp_url_1', None)

        if ENV == 'Linux':
            self.video_path_dir = cfg_dict['video_path_dir_linux']
        else:
            self.video_path_dir = eval(cfg_dict['video_path_dir_win'])
        return

    def setUp(self, sql_list_f) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport(self.project_name)
        self.mysql = Mysql()
        self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)

        self.ai_sport.reset_kafka_to_lastest()
        self.test_result = 'FAIL'
        self.mysql.update_sql(sql_list_f)
        return

    def run_one_file(self, project_id, file_name):
        result_file = os.path.join (LOG_DIR, 'sit_up.yaml')

        if '.mp4' not in file_name:
            return
        if ENV == 'Linux':
            pass
        else:
            file_name = file_name.replace ('/', '\\')

        is_loop = self.result_dic.get ('is_loop', True)

        my_log.info (f'file_name:{file_name}')
        base_name = os.path.basename (file_name)

        file_str = readFile.read_file_str (result_file)

        if base_name in file_str:
            my_log.info (f'file already test:{file_name}')
            return

        self.ffmpeg_1 = start_fake_camera_simple (file_name, is_loop=True, whole_rtsp=self.whole_rtsp)
        # self.ai_sport.reset_kafka_to_lastest()

        topic = self.result_dic.get ('topic', 'se_voice')
        result_msg = self.result_dic.get ('result_msg', None)
        timeout = self.result_dic.get ('timeout', 120)

        # result check
        cheat_count = 0
        score = 0
        self.test_result = 'PASS'
        if result_msg:
            key_words = [result_msg]
            cheat_count, score = self.ai_sport.receive_count_kafka_message (key_words=key_words, topic=topic,
                                                                            timeout=int (timeout))
            my_log.info (f'cheat_count:{cheat_count}, score:{score}')

        file_dict = {'cheat': cheat_count,
                     'score': score}

        file_dict = {f'{file_name}': file_dict}
        my_log.info (f'file_dict:{file_dict}')

        target_dict = {}
        if os.path.exists (result_file):
            target_dict = readFile.read_yaml_dict (result_file)

        if target_dict:
            target_dict.update (file_dict)
        else:
            target_dict = file_dict

        ret = readFile.dump_file (result_file, target_dict)

        self.ffmpeg_1.stop ()
        return

    def run_one_dir(self, project_id, dir_name, file_list):
        for file_name in file_list:
            self.mysql.set_test_project_db (proj_name=self.project_name, is_disabled=0, is_free_mode=True)
            if '.mp4' not in file_name:
                continue
            file_name = os.path.join (self.video_path_dir, dir_name, file_name)
            self.run_one_file(project_id, file_name)

        return

    def run_one_loop(self, project_id,):
        total_list = os.listdir (self.video_path_dir)
        for item in total_list:
            obj_name = os.path.join (self.video_path_dir, item)
            if os.path.isdir (obj_name):
                file_list = os.listdir (obj_name)
                self.run_one_dir (project_id, item, file_list)
            else:
                self.run_one_file (project_id, obj_name)

        return

    def test_run(self, open_dict, result_dic):
        """
        自由模式项目开启
        """
        # 第一步：老师登录AI智能操场平台
        res_log = self.ai_sport.login ()
        log_msg = res_log[0]['msg']
        assert log_msg == "操作成功", "登录成功"

        # check project status
        project_id = self.ai_sport.config (project_name=self.project_name)
        self.project_id = project_id
        self.result_dic = result_dic

        # close free mode must
        self.locationId = open_dict.get ('locationId', None)
        self.ai_sport.close_free_mode(self.locationId, project_id)

        # send OpenProj
        self.test_mode = result_dic.get ('test_mode', None)
        my_log.info (f'result_dic:{result_dic}')
        my_log.info (f'test_mode:{self.test_mode}')
        task_content_id = self.ai_sport.open_proj_by_dict(open_dict, self.test_mode)

        # push video
        if self.video_path_1:
            my_log.info ("开始推送视频")
            self.ffmpeg_1 = start_fake_camera_simple (self.video_path_1, is_loop=False, whole_rtsp=self.whole_rtsp)

        self.run_one_loop (project_id)

        total_list = list()
        for item in self.video_path_dir:
            if ENV == 'Linux':
                pass
            else:
                item = eval (item)
            files = os.listdir(item)
            for index in files:
                file = os.path.join(item, index)
                total_list.append(file)

        # total_list = [r'D:\99_TEST_VIDEO\郑州商学院\2024_10_14\2024_10_14_11_16_6_192.168.2.129_1_3_E.mp4']
        file_count = len(total_list)
        my_log.info (f'file_count:{file_count}')

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