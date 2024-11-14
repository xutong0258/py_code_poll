# coding=utf-8

import os
import sys
import logging
import datetime

BASEDIR = os.path.dirname(os.path.dirname(__file__))
BASEDIR = os.path.dirname(os.path.dirname(BASEDIR))
BASEDIR = os.path.dirname(BASEDIR)

# print(f'BASEDIR:{BASEDIR}')
sys.path.append(BASEDIR)


from common.contants import LOG_DIR


# 读取配置文件中的数据
level = 'DEBUG'
f_level = 'DEBUG'
s_level = 'DEBUG'
filename = 'test.log'
time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
filename = f'{filename}_{time_stamp}.log'
# 获取日志文件的绝对路径
file_path = os.path.join(LOG_DIR, filename)

# print(f'LOG_DIR:{LOG_DIR}')

if not os.path.exists(LOG_DIR):
    # print(f'os.mkdir:{LOG_DIR}')
    os.mkdir(LOG_DIR)

class MyLogger(object):

    @staticmethod
    def create_logger():
        # 一、创建一个名为：python24的日志收集器
        my_log = logging.getLogger("test")
        # 二、设置日志收集器的等级
        my_log.setLevel(level)
        # 三、添加输出渠道（输出到控制台）
        # 1、创建一个输出到控制台的输出渠道
        sh = logging.StreamHandler()
        # 2、设置输出等级
        sh.setLevel(s_level)
        # 3、将输出渠道绑定到日志收集器上
        my_log.addHandler(sh)
        # 四、添加输出渠道（输出到文件）
        fh = logging.FileHandler(file_path, encoding="utf8")
        fh.setLevel(f_level)
        my_log.addHandler(fh)
        # 五、设置日志输出的格式
        # 创建一个日志输出格式
        formatter = logging.Formatter('%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s: %(message)s')
        formatter = logging.Formatter('%(asctime)s-[%(filename)s:%(lineno)d] %(message)s')
        # formatter = logging.Formatter ('[%(filename)s:%(lineno)d] %(message)s')
        # 将输出格式和输出渠道进行绑定
        sh.setFormatter(formatter)
        fh.setFormatter(formatter)

        return my_log


# 调用类的静态方法，创建一个日志收集器
my_log = MyLogger.create_logger()

# my_log = init_logger('hello', file_path)