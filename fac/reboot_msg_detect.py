# coding=utf-8

import os
import sys
import json
import time
import unittest
import warnings
import platform
import re

file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)
base_name = os.path.basename(path_dir)

while 'se-autotest' not in base_name:
    path_dir = os.path.dirname(path_dir)
    base_name = os.path.basename(path_dir)

sys.path.append(path_dir)

from util import *
from common.rtsp import *
import readFile

# from common.mylogger import my_log
from component.ai_sport import *
from component.mysql import Mysql
from common.contants import *



class Reboot_Msg_Common():
    def __init__(self, path_dir,):
        my_log.info(f'path_dir:{path_dir}')
        self.path_dir = path_dir


        return

    def setUp(self, sql_list) -> None:
        my_log.info(f"================{__file__} 测试开始 ===================")
        warnings.simplefilter('ignore', ResourceWarning)

        self.ai_sport = AiSport()
        # self.mysql = Mysql()
        # self.mysql.set_test_project_db(proj_name=self.project_name, is_disabled=0, is_free_mode=True)

        self.test_result = 'FAIL'
        # self.mysql.update_sql(sql_list)
        # self.ai_sport.reset_kafka_to_lastest()
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

    def run_one_loop(self,  result_dic):

        topic = result_dic.get ('topic', 'se_voice')
        result_msg = result_dic.get ('result_msg', None)
        expect_core = result_dic.get ('expect_core')
        skip_assert = result_dic.get ('skip_assert', True)
        timeout = result_dic.get('timeout', 500)
        reverse_flag = result_dic.get ('reverse_flag', False)

        if result_msg:
            # result check
            key_words = ['"messageContentType":71']
            # key_words = [result_msg]
            msg_71 = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int(timeout))
            my_log.info (f'msg_71:{msg_71}')

            self.ai_sport.reset_kafka_to_lastest()
            key_words = ['"messageComment": "openProjFreeMode"']
            # key_words = [result_msg]
            msg_open = self.ai_sport.get_kafka_message (key_words=key_words, topic=topic, timeout=int(timeout))
            my_log.info (f'msg_open:{msg_open}')

            if msg_71 and msg_open:
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

    def test_run(self):
        # alredy reboot no need
        if current_enable:
            rebot_cmd = 'sudo supervisorctl restart   yskj_ai && cd  /home/yskj/data/sport-ci/docker/new  && sudo docker-compose restart'
            cmd = f'ssh yskj@192.168.2.237 {rebot_cmd}'
            my_log.info (f'cmd:{cmd}')
            cmd_excute (cmd)

            # java reboot need 5 mins
            max = 5
            for index in range (max):
                my_log.info (f'index:{index}')
                time.sleep (60)

        cmd = f"scp yskj@192.168.2.237:/home/yskj/data/sport-ci/log/ai_log.txt /home/yskj/"
        result, errors, return_code = cmd_excute (cmd)
        my_log.info (f'result:{result}')
        my_log.info (f'errors:{errors}')
        my_log.info (f'return_code:{return_code}')

        content = '"messageContentType":71'
        cmd = f"cd /home/yskj && grep -rn '{content}' ai_log.txt"
        my_log.info (f'cmd:{cmd}')
        result, errors, return_code = cmd_excute (cmd)
        my_log.info (f'result:{result}')
        my_log.info (f'errors:{errors}')
        my_log.info (f'return_code:{return_code}')

        result = result.decode ('utf-8').strip ('\r\n')
        my_log.info (f'result:{result}')

        pattern = r".*?:"
        match = re.search(pattern, result)
        line_1 = None
        if match:
            line_1 = match.group(0)
            my_log.info (f'line_1:{line_1}')
            line_1 = line_1.replace(':', '')
            my_log.info (f'line_1:{line_1}')
        else:
            my_log.info ("No match found")

        content = 'openProjFreeMode'
        cmd = f"cd /home/yskj && grep -rn '{content}' ai_log.txt"

        my_log.info (f'cmd:{cmd}')
        result, errors, return_code = cmd_excute (cmd)
        my_log.info (f'result:{result}')
        my_log.info (f'errors:{errors}')
        my_log.info (f'return_code:{return_code}')
        text = "This is a sample text with some words."
        pattern = r".*?:"
        result = result.decode ('utf-8').strip ('\r\n')
        match = re.search(pattern, result)
        line_2 = None
        if match:
            line_2 = match.group(0)
            my_log.info (f'line_2:{line_2}')
            line_2 = line_2.replace(':', '')
            my_log.info (f'line_2:{line_2}')
        else:
            my_log.info ("No match found")

        self.test_result = 'PASS'

        # openProjFreeMode message before "messageContentType":71
        if line_1 and line_2 and int(line_2) < int(line_1):
            self.test_result = 'FAIL'

        dict_para = {
            'project_name': '开机消息检测',
            'test_name': '"messageContentType":71',
            'test_result': self.test_result,
            'test_mode': f'free_mode'
        }

        readFile.update_result (LOG_DIR, dict_para)
        return


    def tearDown(self) -> None:
        # 退出AI智慧平台
        self.ai_sport.logout()
        assert self.test_result == 'PASS', 'CASE FAIL'
        my_log.info(f"================{__file__} 测试结束 ===================")


if __name__ == '__main__':
    pass
