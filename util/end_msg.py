
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

from common import dingding
import readFile
from util import *
from common.contants import *
from readFile import *

root_dir = os.path.dirname(path_dir)
file = os.path.join(root_dir, 'ws_cfg.yaml')
cfg_dict = None
if os.path.exists(file):
    cfg_dict = readFile.read_yaml_dict(file)

def get_sanity_msg():
    msg = ''
    file = os.path.join(LOG_DIR, 'message_detect.yaml')
    if os.path.exists(file):
        result_dict = readFile.read_yaml_dict(file)
        msg =  '\n\n' + '<font color="#0000FF">**开机消息检测:**</font>' + str(result_dict)
        msg = msg.replace ('{', '\n\n ')
        msg = msg.replace (',', '\n\n')
        msg = msg.replace ('}', '')
        # print(f'{msg}')

    file = os.path.join(LOG_DIR, 'we_chat_result.yaml')
    if os.path.exists(file):
        result_dict = readFile.read_yaml_dict(file)
        msg =  msg + '\n\n' + '<font color="#0000FF">**微信小程序:**</font>' + str(result_dict)
        msg = msg.replace ('{', '\n\n ')
        msg = msg.replace (',', '\n\n')
        msg = msg.replace ('}', '')
        # print(f'{msg}')

    file = os.path.join(LOG_DIR, 'face_mode_result.yaml')
    if os.path.exists(file):
        result_dict = readFile.read_yaml_dict(file)
        msg = msg + '\n\n' + '<font color="#0000FF">**人脸模式:**</font>' + str(result_dict)
        msg = msg.replace ('{', '\n\n ')
        msg = msg.replace (',', '\n\n')
        msg = msg.replace ('}', '')
        # print(f'{msg}')

    file = os.path.join(LOG_DIR, 'free_mode_result.yaml')
    if os.path.exists(file):
        result_dict = readFile.read_yaml_dict(file)
        msg = msg + '\n\n' + '<font color="#0000FF">**自由模式:**</font>' + str (result_dict)
        msg = msg.replace ('{', '\n\n ')
        msg = msg.replace (',', '\n\n')
        msg = msg.replace ('}', '')
    else:
        print(f'file not exist: {file}')

    return msg


def dict_to_msg(result_dict):
    msg = ''
    for key, value in result_dict.items ():
        msg = msg + f'<font color="#0000FF">**{key}**</font>: \n\n'
        # print(f"{key}: {value}")
        if not isinstance (value, dict):
            continue
        for sub_key, sub_value in value.items ():
            msg = msg + f"&nbsp;&nbsp;&nbsp;{sub_key}: {sub_value}\n\n"
        msg = msg + f'\n\n'
    # print (f'msg: {msg}')
    return msg

def get_foul_msg():
    msg = ''
    tmp_msg = ''
    project_list = ['立定跳远', '引体向上', '仰卧起坐', '坐位体前屈', '跳绳', '50米', '实心球']

    for item in project_list:
        file = project_foul_file_map.get(item, None)
        file = os.path.join (LOG_DIR, file)
        # print (f'file:{file}')
        if file and os.path.exists(file):
            result_dict = readFile.read_yaml_dict(file)
            msg = msg + f'<font color="#0000FF">**{item}**</font>: \n\n'
            for sub_key, sub_value in result_dict.items ():
                msg = msg + f"&nbsp;&nbsp;&nbsp;{sub_key}: {sub_value}\n\n"
            msg = msg + f'\n\n'

    # print(f"{msg}")
    return msg

def main():
    test_type = 'FOUL_FACE_TEST'
    debug_mode = False
    if debug_mode:
        target_server = '202'
    else:
        if len(sys.argv) < 3:
            print('return')
            return
        target_server = sys.argv[1]
        test_type = sys.argv[2]

    if test_type == 'SANITY_TEST':
        msg = get_sanity_msg()
    else:
        msg = get_foul_msg()

    print(f'{msg}')
    dingding.send_end_dingding(msg, test_type=test_type, target_server=target_server)

    # set flag
    if test_type == 'FOUL_FACE_TEST':
        test_flag_dic = {f'{target_server}': 'END'}
        file = os.path.join(root_dir, 'test_flag.yaml')
        readFile.dump_file(file, test_flag_dic)
    return

if __name__ == "__main__":
    main()
