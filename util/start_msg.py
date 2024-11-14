
# coding=utf-8

import os
import sys
import json
import time
import unittest
import warnings
import platform
import datetime


file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)
base_name = os.path.basename(path_dir)

while 'se-autotest' not in base_name:
    path_dir = os.path.dirname(path_dir)
    base_name = os.path.basename(path_dir)

sys.path.append(path_dir)

from component.ai_sport import *

from common import dingding
import readFile
from util import *

root_dir = os.path.dirname(path_dir)
file = os.path.join(root_dir, 'ws_cfg.yaml')
cfg_dict = None
if os.path.exists(file):
    cfg_dict = readFile.read_yaml_dict(file)

# dump version
ai_sport = AiSport()
ai_sport.login()
url = f'{WEB_IP}/main_version'
# print(f'url:{url}')
result = ai_sport.http_requst_get(url)
file = os.path.join(LOG_DIR, 'version.yaml')
readFile.dump_file(file, result)
ai_sport.logout()

fac_init_result_dic = {
            '50米': 'TODO',
            '800米': 'TODO',
            '仰卧起坐': 'TODO',
            '坐位体前屈': 'TODO',
            '实心球': 'TODO',
            '引体向上': 'TODO',
            '立定跳远': 'TODO',
            '跳绳': 'TODO'
           }


free_init_result_dic = {
            '50米': 'TODO',
            '铅球': 'TODO',
            '仰卧起坐': 'TODO',
            '坐位体前屈': 'TODO',
            '实心球': 'TODO',
            '引体向上': 'TODO',
            '立定跳远': 'TODO',
            '跳绳': 'TODO',
            '阳光跑': 'TODO',
           }

def main():
    if len(sys.argv) < 3:
        return

    target_server = sys.argv[1]
    test_type = sys.argv[2]

    # dump txt
    cmd = f'cd /home/yskj/data/sport-ci/log && tail -F ai_log.txt | tee hello.txt'

    # set flag
    test_flag_dic = {f'{target_server}': 'START'}
    file = os.path.join(root_dir, 'test_flag.yaml')
    readFile.dump_file(file, test_flag_dic)

    if target_server == '201':
        # cfg_dict.update({'TEST_SERVER': f'192.168.2.237'})
        pass
    else:
        pass
        # cfg_dict.update({'TEST_SERVER': f'237'})

    file = os.path.join(root_dir, 'ws_cfg.yaml')
    readFile.dump_file(file, cfg_dict)

    if 'SANITY_TEST' == test_type:
        file = os.path.join (LOG_DIR, 'face_mode_result.yaml')
        readFile.dump_file (file, fac_init_result_dic)
        file = os.path.join (LOG_DIR, 'free_mode_result.yaml')
        readFile.dump_file (file, free_init_result_dic)
    else:
        cmd = f'cd {LOG_DIR}; rm -rf *foul.yaml'
        cmd_excute(cmd)
        pass

    dingding.send_start_dingding(test_type=test_type, target_server=target_server)
    return

def end_msg_prepare(test_type='SANITY_TEST'):
    TOTAL_RESULT = {}
    msg = ''
    file = os.path.join(LOG_DIR, 'class_list_result.yaml')
    if os.path.exists(file):
        result_dict = readFile.read_yaml_dict(file)
        TOTAL_RESULT.update({"随堂名单模式": result_dict})
        msg = "随堂名单模式: " + str(result_dict)

    file = os.path.join(LOG_DIR, 'face_mode_result.yaml')
    if os.path.exists(file):
        result_dict = readFile.read_yaml_dict(file)
        TOTAL_RESULT.update({"随堂人脸模式": result_dict})
        msg = msg + '\n' + "随堂人脸模式: " + str(result_dict)

    file = os.path.join(LOG_DIR, 'free_mode_result.yaml')
    if os.path.exists(file):
        result_dict = readFile.read_yaml_dict(file)
        TOTAL_RESULT.update({"自由模式": result_dict})
        if test_type == 'SANITY_TEST':
            msg = msg + '\n' + "自由模式: " + str(result_dict)
        else:
            msg = msg + '\n' + str(result_dict)
    else:
        print(f'file not exist: {file}')
    msg = msg.replace('}}', 'END')
    msg = msg.replace('},', '}')
    msg = msg.replace('}', '}\n')
    msg = msg.replace('END', '}}')
    return msg

if __name__ == "__main__":
    main()
    pass
