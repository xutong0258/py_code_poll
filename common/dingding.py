# coding=utf-8

import json
import os
import sys
import logging
import subprocess
import time
from subprocess import *
import requests
import platform
import datetime
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)
base_name = os.path.basename(path_dir)

while 'se-autotest' not in base_name:
    path_dir = os.path.dirname(path_dir)
    base_name = os.path.basename(path_dir)

sys.path.append(path_dir)

import readFile
from util import *
from common.contants import *

root_dir = os.path.dirname(path_dir)
file = os.path.join(root_dir, 'ws_cfg.yaml')
cfg_dict = None
if os.path.exists(file):
    cfg_dict = readFile.read_yaml_dict(file)

init_file_count = 0
def send_start_dingding(test_type='SANITY_TEST', target_server='202'):
    file = os.path.join(LOG_DIR, 'version.yaml')
    version_dict = readFile.read_yaml_dict(file)
    version = version_dict['data']
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'SANITY_TEST' == test_type:
        header = f'<font color="#0000FF">**autotest:Sanity Test START...**</font>'
    elif 'FOUL_FREE_TEST' == test_type:
        header = f'<font color="#0000FF">**autotest:自由模式负样本测试开始...**</font>\n\n'
    elif 'FOUL_FACE_TEST' == test_type:
        header = f'<font color="#0000FF">**autotest:人脸模式负样本测试开始...**</font>\n\n'
    else:
        header = f'<font color="#0000FF">**autotest:负样本测试开始...**</font>'

    send_msg = header + f"{time_stamp}" + '\n\n' + version + '\n\n'

    headers = {'Content-Type': 'application/json;charset=utf-8'}

    data = {
        "msgtype": "markdown",  # 设置消息类型为Markdown
        "markdown": {
            "title": test_type,  # 设置Markdown标题
            "text": f'Monitor:{send_msg}'  # 设置Markdown正文
        }
    }
    print("准备发送告警信息:" + send_msg)
    url = cfg_dict[f'{target_server}']['dingding_url']
    # url = f'https://oapi.dingtalk.com/robot/send?access_token=a809907d5498a7f4ab1bff6eb91da67b7a99c595ab8164ac62b41e8f7c6c964c'
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print("告警信息发送结果:" + r.text)

    reboot_log_check(is_init=True)
    return

def send_end_dingding(msg, test_type='SANITY_TEST', target_server='202'):
    file = os.path.join(LOG_DIR, 'version.yaml')
    version_dict = readFile.read_yaml_dict(file)
    version = version_dict['data']
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'SANITY_TEST' == test_type:
        header = f'<font color="#0000FF">**autotest:Sanity Test END...**</font>\n\n'
    elif 'FOUL_FREE_TEST' == test_type:
        header = f'<font color="#0000FF">**autotest:自由模式负样本测试结束...**</font>\n\n'
    elif 'FOUL_FACE_TEST' == test_type:
        header = f'<font color="#0000FF">**autotest:人脸模式负样本测试结束...**</font>\n\n'
    else:
        header = f'<font color="#0000FF">**autotest:人脸模式负样本测试结束...**</font>\n\n'

    send_msg = header + f"{time_stamp}" + '\n\n' + version + '\n\n' + msg
    headers = {'Content-Type': 'application/json;charset=utf-8'}

    red_msg = '<font color="#dd0000"> FAIL </font>'
    send_msg = send_msg.replace('FAIL', f'{red_msg}')
    # "text": f'Monitor:{send_msg}'  # 设置Markdown正文
    data = {
        "msgtype": "markdown",  # 设置消息类型为Markdown
        "markdown": {
            "title": test_type,  # 设置Markdown标题
            "text": f'Monitor:{send_msg}'  # 设置Markdown正文
        }
    }

    # print("准备发送告警信息:" + msg)
    url = cfg_dict[f'{target_server}']['dingding_url']
    # url = f'https://oapi.dingtalk.com/robot/send?access_token=a809907d5498a7f4ab1bff6eb91da67b7a99c595ab8164ac62b41e8f7c6c964c'
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print("告警信息发送结果:" + r.text)

    reboot_log_check()
    return

def reboot_log_check(is_init=False):
    global init_file_count

    cmd = 'ssh yskj@192.168.2.237 ls -l /home/yskj/data/sport-ci/log/C++ | wc -l'
    result, errors, return_code = cmd_excute (cmd)
    print (f'result:{result}')

    file_count =  int(result.decode("utf8"))
    print (f'file_count:{file_count}')
    if is_init:
        init_file_count = int(file_count)
    elif file_count > init_file_count:
        time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")
        msg = f"autotest: sanity CPP reboot happened:{time_stamp}"
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            "msgtype": "text",
            "text": {
                "content": msg
            }
        }
        print ("准备发送告警信息:" + msg)
        # url = f'https://oapi.dingtalk.com/robot/send?access_token=a809907d5498a7f4ab1bff6eb91da67b7a99c595ab8164ac62b41e8f7c6c964c'
        url = cfg_dict['237']['dingding_url']
        r = requests.post (url, data=json.dumps (data), headers=headers)
        print ("告警信息发送结果:" + r.text)
    else:
        time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")
        msg = f"autotest: sanity hasn't reboot happened:{time_stamp}"
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            "msgtype": "text",
            "text": {
                "content": msg
            }
        }
        print ("准备发送告警信息:" + msg)
        # url = f'https://oapi.dingtalk.com/robot/send?access_token=a809907d5498a7f4ab1bff6eb91da67b7a99c595ab8164ac62b41e8f7c6c964c'
        url = cfg_dict['237']['dingding_url']
        r = requests.post (url, data=json.dumps (data), headers=headers)
        print ("告警信息发送结果:" + r.text)
    return


def monitor_cpp():
    # STACKDUMP
    monitor_list = ['空指针', 'STACKDUMP', '程序开始启动', '未获取到卡的配置消息']
    log_check_list = ['"projectType": 7', '"projectType": 8', '"projectType": 22', '"projectType": 23', '"messageContentType":4,']

    if current_enable:
        # 未获取到卡的配置消息
        item = '未获取到卡的配置消息'
        cmd = f"cd /home/yskj/data/sport-ci/log/C++ && grep -rn {item}"
        print (f'cmd:{cmd}')
        result, errors, return_code = cmd_excute (cmd)
        print (f'result:{result}')
        if result:
            time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")
            msg = f"Monitor: {item}:{time_stamp}"
            headers = {'Content-Type': 'application/json;charset=utf-8'}
            data = {
                "msgtype": "text",
                "text": {
                    "content": msg
                }
            }
            print ("准备发送告警信息:" + msg)
            # url = f'https://oapi.dingtalk.com/robot/send?access_token=a809907d5498a7f4ab1bff6eb91da67b7a99c595ab8164ac62b41e8f7c6c964c'
            url = cfg_dict['237']['dingding_url']
            r = requests.post (url, data=json.dumps (data), headers=headers)
            print ("告警信息发送结果:" + r.text)
            return

    path = '/home/yskj/data/sport-ci/log/C++'
    files = os.listdir(path)
    init_file_count = len(files)
    print (f'init_file_count:{init_file_count}')

    sleep_time = 60 * 6 # 6 min
    monitor_list = ['队列溢出']
    monitor_list = None
    while True:
        path = '/home/yskj/data/sport-ci/log/C++'
        files = os.listdir(path)
        file_count = len (files)
        print (f'file_count:{file_count}')
        if file_count > init_file_count:
            time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")
            msg = f"Monitor: CPP reboot happened:{time_stamp}"
            headers = {'Content-Type': 'application/json;charset=utf-8'}
            data = {
                "msgtype": "text",
                "text": {
                    "content": msg
                }
            }
            print ("准备发送告警信息:" + msg)
            # url = f'https://oapi.dingtalk.com/robot/send?access_token=a809907d5498a7f4ab1bff6eb91da67b7a99c595ab8164ac62b41e8f7c6c964c'
            url = cfg_dict['237']['dingding_url']
            r = requests.post (url, data=json.dumps (data), headers=headers)
            print ("告警信息发送结果:" + r.text)
            break
        if not monitor_list:
            # restart push video
            cmd = f"sudo docker run --rm -itd  --name rtsp-server -e MTX_PROTOCOLS=tcp -p 8554:8554  file.yishikj.cn:8888/zhty/rtsp-simple-server:v1"
            # result, errors, return_code = cmd_excute (cmd)
            # print (f'restart push video result:{result}')
            time.sleep (sleep_time)
            continue
        for item in monitor_list:
            cmd = f"cd /home/yskj/data/sport-ci/log/C++ && grep -rn {item}"
            print (f'cmd:{cmd}')
            result, errors, return_code = cmd_excute (cmd)
            print (f'result:{result}')
            if result:
                time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")
                msg = f"Monitor: {item}:{time_stamp}"
                headers = {'Content-Type': 'application/json;charset=utf-8'}
                data = {
                    "msgtype": "text",
                    "text": {
                        "content": msg
                    }
                }
                print ("准备发送告警信息:" + msg)
                # url = f'https://oapi.dingtalk.com/robot/send?access_token=a809907d5498a7f4ab1bff6eb91da67b7a99c595ab8164ac62b41e8f7c6c964c'
                url = cfg_dict['237']['dingding_url']
                r = requests.post (url, data=json.dumps (data), headers=headers)
                print ("告警信息发送结果:" + r.text)

    return


if __name__ == '__main__':
    monitor_cpp()
    # reboot_log_check (True)
    # reboot_log_check()
    pass
