# coding=utf-8

import json
import os
import shutil
import sys
import logging
import subprocess
import time
from subprocess import *
import datetime

file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)


PROGRAM = 'Hello'

formatter2 = logging.Formatter(
'[%(asctime)s]'
'%(filename)s'
'[Line:%(lineno)d]: '
'%(message)s')

CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
CH.setFormatter(formatter2)


LOG = logging.getLogger(PROGRAM)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(CH)

_format =('[%(asctime)s][%(filename)s][%(funcName)s][%(lineno)s]'
' %(levelname)s: %(message)s')

def init_logger(loggername, file=None):
    logger = logging.getLogger(loggername)
    logger.setLevel(level=logging.DEBUG)
     # print("logger.handlers:", logger.handlers)
    if not logger.handlers:
       if file:
          file_handler = logging.FileHandler(file)
          file_format = logging.Formatter(_format)
          file_handler.setFormatter(file_format)
          file_handler.setLevel(logging.DEBUG)
          logger.addHandler(file_handler)
    return logger

# os.system
def cmd_excute(cmd, logger=None, outfile=None, errfile=None):
    if outfile is None and errfile is None:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        # result = stdout.decode('utf-8').strip('\r\n')
        result = stdout
        errors = stderr
        return_code = process.returncode
        msg = result if not stderr else errors
        if logger:
            logger.info(cmd)
            logger.debug(return_code)
            if return_code != 0:
                logger.error(errors)

        return result, errors, return_code
    else:
        f_out = open(outfile, 'w')
        f_err = open(errfile, 'w')
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=f_out,
            stderr=f_err)
        output, errors = process.communicate()
        return_code = process.returncode
        if logger:
            logger.info(cmd)
            logger.debug(return_code)
        if return_code != 0:
            logger.error(errors)

        return return_code

def hello():
    str_cmd = 'dir'
    result, errors, return_code = cmd_excute(str_cmd, LOG)
    LOG.info(f'result:{result}')
    print('hello')
    return

def convert_file():
    video_path_dir = r"D:\99_TEST_VIDEO\3_sit_forward_test"
    video_path_dir = os.getcwd()
    files = os.listdir(video_path_dir)
    str_cmd = f'cd {video_path_dir}'

    result, errors, return_code = cmd_excute(str_cmd)
    LOG.info(f'result:{result}, errors:{errors}, return_code:{return_code}')

    for file_name in files:
        if '.mp4' not in file_name:
            continue
        print(f'file_name:{file_name}')
        # out_file = file_name.replace('.mp4', '_output.mp4')
        out_file = os.path.join(video_path_dir, 'output', file_name)
        str_cmd = f'ffmpeg -i {file_name} -c:v libx265 -c:a copy {out_file}'
        result, errors, return_code = cmd_excute(str_cmd)
        LOG.info(f'result:{result}, errors:{errors}, return_code:{return_code}')
        print('hello')
    return

def replace_file():
    wait_str = '192.168.2.235'
    target_str = '192.168.2.17'
    current_dir = os.getcwd()
    target_dirs = os.listdir(current_dir)
    final_list = []
    for item in target_dirs:
        path = os.path.join(current_dir, item)
        command = f"cd {path} && sed -i 's/{wait_str}/{target_str}/g' *.yaml"
        cmd_excute(command)

    return

def clean_file():
    C1_Time = datetime.datetime.now ()
    print(f'curreent:{C1_Time}')
    time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")
    print(f'time_stamp:{time_stamp}')

    # current_dir = os.getcwd()
    for root, dirs, files in os.walk(path_dir):
        for file in files:
            if '.mp4' not in file:
                continue
            file = os.path.join(root, file)

            c2_Time = os.path.getmtime(file)
            c2_Time = datetime.datetime.fromtimestamp(c2_Time)
            delta = C1_Time.__sub__ (c2_Time)
            print(f'delta.days:{delta.days}')
            if delta.days > 5:
                print (f"remove file:{file} delta.days:{delta.days}")
                cmd = f'sudo rm -rf {file}'
                cmd_excute(file)
    return

def copy_file():
    C1_Time = datetime.datetime.now ()
    print(f'curreent:{C1_Time}')
    time_stamp = datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S")
    print(f'time_stamp:{time_stamp}')

    # current_dir = os.getcwd()
    for root, dirs, files in os.walk(path_dir):
        for file in files:
            if '203' in file:
                dest_file = os.path.join(path_dir, '../total', file)
                source_file = os.path.join(root, file)
                shutil.copyfile(source_file, dest_file)

    return

def install_package_by_file():
    file_name = 'requirements.txt'
    with open (file_name, "r") as file:
        for line in file:
            line = line.strip()
            cmd = f'sudo pip install {line} -i https://mirrors.aliyun.com/pypi/simple/'
            result, errors, return_code = cmd_excute (cmd)
            LOG.info (f'result:{result}, errors:{errors}, return_code:{return_code}')

if __name__ == '__main__':
    # replace_file()
    # copy_file()
    # convert_file()
    # install_package_by_file()
    pass
