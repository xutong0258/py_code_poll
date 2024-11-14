# coding=utf-8
import os
import sys
import re
import platform
import datetime

file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)
base_name = os.path.basename(path_dir)

while 'se-autotest' not in base_name:
    path_dir = os.path.dirname(path_dir)
    base_name = os.path.basename(path_dir)

sys.path.append(path_dir)

import readFile

# root
root_dir = os.path.dirname(path_dir)
file = os.path.join(root_dir, 'ws_cfg.yaml')
cfg_dict = None
if os.path.exists(file):
    cfg_dict = readFile.read_yaml_dict(file)

from case_data.stand_jump_v import *
from case_data.long_run_v import *
from case_data.pull_up_v import *
from case_data.sit_up_v import *
from case_data.sit_forward_v import *
from case_data.rope_skip_v import *
from case_data.solid_ball_v import *
from case_data.shot_ball_v import *
from case_data.sun_run_v import *

TEST_MODE = 'UNIT_TEST'
TEST_SERVER = '192.168.2.237'
if cfg_dict:
    TEST_MODE = cfg_dict.get('TEST_MODE', 'UNIT_TEST')
    print(f"TEST_MODE:{TEST_MODE}")
    TEST_SERVER = cfg_dict.get('TEST_SERVER', '192.168.2237')

# 项目目录的路径 | 如果运行的时候项目目录路径出错，使用上面abspath的方式来获取当前文件的绝对路径
BASEDIR = os.path.dirname(os.path.dirname(__file__))
# 配置文件的路径
CONF_DIR = os.path.join(BASEDIR, "conf")
COMMON_DIR = os.path.join(BASEDIR, "common")
# 用例数据的目录
DATA_DIR = os.path.join(BASEDIR, "data")
# 日志文件目录
LOG_DIR = os.path.join(BASEDIR, "../auto_test_log")

# 测试报告的路
REPORT_DIR = os.path.join(BASEDIR, "reports")

prepare_video_path()

current_enable = False


file = os.path.join(CONF_DIR, f"conf.yaml")
ENV_DICT = readFile.read_yaml_dict(file)
# print(f'ENV_DICT:{ENV_DICT}')

LOGIN_DATA = ENV_DICT.get ('login_data', None)
# print (f'login_data:{LOGIN_DATA}')

USER = LOGIN_DATA.get('loginName', None)
# print(f'USER:{USER}')

PWD = LOGIN_DATA.get('password', None)
# print(f'PWD:{PWD}')


WEB_IP = eval(ENV_DICT.get('WEB_IP', None))
# print (f'WEB_IP:{WEB_IP}')

we_xin_cfg = ENV_DICT.get('we_xin_cfg', None)
we_xin_hot = we_xin_cfg.get('host', None)