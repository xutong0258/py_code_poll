#!/usr/bin/python3
# coding=utf-8
# Author : anson
# Toutiao : code日志
# Time : 2020-2-26

import json
import os
import subprocess
import time
import datetime
import configparser
# import psutil
import requests

# 配置文件
root_path = os.path.abspath(os.path.dirname(__file__)) + os.sep
config = root_path + 'config.ini'

# 初始化配置（阈值，进程，钉钉）
def init_conf():
    cf = configparser.ConfigParser()
    cf.read(config, encoding='utf-8')
    threshold = cf.items('Threshold')
    processlist = cf.items('Process')
    dingding = cf.items('Dingding')

    # 阈值配置
    threshold_map = {}
    for i in threshold:
        threshold_map[i[0]] = int(i[1])

    # 进程
    process_map = {}
    for i in processlist:
        process_map[i[0]] = i[1].split('#')

    # 钉钉配置
    dingding = cf.items('Dingding')
    dingding_map = {}
    for i in dingding:
        dingding_map[i[0]] = i[1]
    return [threshold_map, dingding_map, process_map]


# 实时信息
def get_alarm_info():
    # 告警频次
    cf = configparser.ConfigParser()
    cf.read(config, encoding='utf-8')
    alarm = cf.items('AlarmConf')
    alarm_map = {}
    for i in alarm:
        alarm_map[i[0]] = int(i[1])
    return alarm_map


# 监控CPU信息
def check_cpu(threshold):
    cpu_per = psutil.cpu_percent(True, True)
    max_cpu = max(cpu_per)
    alarm = True if max_cpu > threshold else False
    return [max_cpu, alarm]


# 监控内存信息
def check_mem(threshold):
    mem = psutil.virtual_memory()  # 查看内存信
    mem_per = int(mem[2])
    alarm = True if mem_per > threshold else False
    return [mem_per, alarm]


def check_process(processlist):
    pro_res = []
    is_alarm_pro = False
    error_msg = ""

    # 遍历配置的进程
    for pro in processlist:
        process_info = str(processlist[pro][0]).split(',')

        process_name = process_info[0]
        cpu_min_value = float(process_info[1])
        mem_max_value = float(process_info[2])

        command = "ps aux | grep '" + process_info[0]  + "' | grep -v grep | awk '{print $2}'"
        popen = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout
        process_id = popen.readline().decode('ascii')

        command = "top -b -n 1 -p " + str(int(process_id)) + " | grep yskj | awk '{print $9,$10}'"

        popen = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout
        strmsg1 = popen.readline().decode('ascii')
        time.sleep(1)

        popen = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout
        strmsg2 = popen.readline().decode('ascii')
        time.sleep(1)

        popen = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout
        strmsg3 = popen.readline().decode('ascii')
        time.sleep(1)

        if strmsg1 != "" and strmsg2 != '' and strmsg3 != '':
            process_text_1 = strmsg1.split(' ')
            process_text_2 = strmsg2.split(' ')
            process_text_3 = strmsg3.split(' ')
            cpunum_1 = float(process_text_1[0])
            memnum_1 = float(process_text_1[1])
            cpunum_2 = float(process_text_2[0])
            memnum_2 = float(process_text_2[1])
            cpunum_3 = float(process_text_3[0])
            memnum_3 = float(process_text_3[1])
            if cpunum_1 < cpu_min_value and cpunum_2 < cpu_min_value and cpunum_3 < cpu_min_value:
                is_alarm_pro = True
                error_msg = error_msg + "进程【" + process_name + "】cpu低于" + str(cpu_min_value) + "%\n"
            if memnum_1 > mem_max_value and memnum_2 > mem_max_value and memnum_3 > mem_max_value:
                is_alarm_pro = True
                error_msg = error_msg + "进程【" + process_name + "】内存超过" + str(mem_max_value) + "%\n"
        elif strmsg1 == "" and strmsg2 == '' and strmsg3 == '':
            is_alarm_pro = True
            error_msg += error_msg + "进程【" + process_name + "】退出了\n"

    return [pro_res, is_alarm_pro, error_msg]


def handle(threshold, dingding, processlist, alarm):
    nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("当前执行时间:" + nowtime)
    pro_res, is_alarm_pro, error_msg = check_process(processlist)
    pro_json_str = json.dumps(pro_res)

    if is_alarm_pro:
        alarm_msg = "【" + dingding['hostname'] + "】服务器出现故障,请尽快处理！\n"
        send_alarm(alarm_msg + error_msg)
    else:
        print("进程运行正常...")

def updateAlarmConf(alarm_times, next_alarm_time):
    cf = configparser.ConfigParser()
    cf.read(config, encoding='utf-8')
    cf.set('AlarmConf', 'alarm_times', str(alarm_times))
    cf.set('AlarmConf', 'next_alarm_time', str(next_alarm_time))
    with open(config, 'w') as f:
        cf.write(f)


def send_alarm(msg):
    # msg = '[' + dingding['keyword'] + "]\n" + msg
    msg = '[' + 'autotest' + "]\n" + msg
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    print("准备发送告警信息:" + msg)
    # url = "https://oapi.dingtalk.com/robot/send?access_token=" + dingding['access_token']
    url = "https://oapi.dingtalk.com/robot/send?access_token=72bedd5c58d83dc4ebd90481a8b178a7bdd043ed0222fbc7490d79c74a032295"
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print("告警信息发送结果:" + r.text)
    return


if __name__ == '__main__':
    send_alarm('Hello')
    # threshold, dingding, processlist = init_conf()
    # alarm = get_alarm_info()
    # handle(threshold, dingding, processlist, alarm)
