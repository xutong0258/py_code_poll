# coding=utf-8
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

file_path = os.path.abspath(__file__)
path_dir = os.path.dirname(file_path)
base_name = os.path.basename(path_dir)

while 'se-autotest' not in base_name:
    path_dir = os.path.dirname(path_dir)
    base_name = os.path.basename(path_dir)

sys.path.append(path_dir)

import readFile

from common.mylogger import my_log
from common.contants import *


camera_list = list()

def stop_fake_camera():
    for item in camera_list:
        # 停止推流
        item.stop()
        my_log.info(f'ffmpeg.stop')
        camera_list.remove(item)


def start_fake_camera_simple(video_path, url_suffix=None, is_loop=True, whole_rtsp=None):
    # 开启进程执行ffmpeg命令，一直推流

    final_rtsp_url =None
    if whole_rtsp:
        final_rtsp_url = whole_rtsp
    else:
        raise ValueError (f"whole_rtsp is None:{whole_rtsp}")
        # rtsp_url = conf.get_str("env", "rtsp_url")
        # final_rtsp_url = rtsp_url + url_suffix

    if os.path.exists(video_path):
        ffmpeg = Ffmpeg(video_path=video_path, rtsp_url=final_rtsp_url, is_loop=is_loop)
        ffmpeg.start()
    else:
        raise ValueError(f"File not exist:{video_path}")

    camera_list.append(ffmpeg)
    return ffmpeg

# ENV = platform.system()
# print(f'ENV:{ENV}')

def start_fake_camera_simple_dir(video_path_dir, whole_rtsp):
    # 开启进程执行ffmpeg命令，一直推流
    while True:
        total_list = list ()
        file_list = os.listdir (video_path_dir)
        for item in file_list:
            file = os.path.join (video_path_dir, item)
            total_list.append (file)

        for file_name in total_list:
            size = os.path.getsize (file_name)
            # print (f"File size: {size} bytes")

            size_m = size / (1024 * 1024)
            size_m = int (size_m)

            ffmpeg = Ffmpeg (video_path=file_name, rtsp_url=whole_rtsp, is_loop=True)
            ffmpeg.start ()
            time.sleep (size_m)
    return

def start_fake_camera_multi_dir(video_path_dir_list, whole_rtsp):
    # 开启进程执行ffmpeg命令，一直推流
    while True:
        total_list = list ()
        print(f'video_path_dir_list:{video_path_dir_list}')
        for dir in video_path_dir_list:
            print (f'dir:{dir}')
            file_list = os.listdir (dir)
            for item in file_list:
                file = os.path.join (dir, item)
                total_list.append (file)

        for file_name in total_list:
            size = os.path.getsize (file_name)
            # print (f"File size: {size} bytes")

            size_m = size / (1024 * 1024)
            size_m = int (size_m)
            print (f'size_m:{size_m}')
            ffmpeg = Ffmpeg (video_path=file_name, rtsp_url=whole_rtsp, is_loop=True)
            ffmpeg.start ()
            size_m = 120
            time.sleep (size_m)
    return

def push_multi_sit_forward_video():
    whole_rtsp = 'rtsp://192.168.2.17:8554/live304'
    if ENV == 'Linux':
        video_path_dir_list = list()
        video_path_dir_list.append ('/home/yskj/data/video/CPP_Stress/03_multi_sit_forward_p1')
        video_path_dir_list.append('/home/yskj/data/video/CPP_Stress/03_sitforward/A')
    else:
        video_path_dir_list = list()
        video_path_dir_list.append(r"D:\99_TEST_VIDEO\CPP_Stress\03_multi_sit_forward_p1")
        video_path_dir_list.append (r"D:\99_TEST_VIDEO\CPP_Stress\03_sitforward\A")

    start_fake_camera_multi_dir(video_path_dir_list, whole_rtsp=whole_rtsp)
    return

class Ffmpeg:
    def __init__(self, video_path, rtsp_url, is_loop=True):
        self.video_path = video_path.replace('\\', '/')
        self.rtsp_url = rtsp_url
        self.process = None
        self.is_loop = is_loop
        return

    def start(self):
        my_log.info("播放视频的地址video_path：{}".format(self.video_path))
        my_log.info("rtsp服务的地址：{}".format(self.rtsp_url))
        # command = f'ffmpeg -re -stream_loop -1 -i {self.video_path}
        # -c copy -f rtsp -rtsp_transport tcp {self.rtsp_url}'
        command = f'ffmpeg -re '
        if self.is_loop:
            command = command + f' -stream_loop -1 '
        command = command + f' -i {self.video_path} '
        command = command + f' -c copy -an -f rtsp -rtsp_transport tcp {self.rtsp_url}'
        # command = command + f' -vf "loop=loop=-1:size=1" -c copy -an -f rtsp -rtsp_transport tcp {self.rtsp_url}'
        # ffmpeg -i input.mp4 -vf "loop=loop=-1:size=1" output.mp4

        my_log.info("执行command的命令：{}".format(command))
        self.process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        return

    def stop(self):
        if self.process is not None:
            self.process.send_signal(signal.SIGTERM)
            time.sleep(1)
            self.process = None

    def push_video_thread(self):
        p_cnt = 1
        pool_list = []
        thread_pool = ThreadPoolExecutor (p_cnt)
        for index in range (0, p_cnt):
            pool_list.append (thread_pool.submit (start_fake_camera_simple, VIDEO_DICT['SOLID_BALL_001_P1'], '161'))
        for fu in as_completed (pool_list):
            res = fu.result ()

        time.sleep (5)
        p_cnt = 1
        pool_list = []
        thread_pool = ThreadPoolExecutor (p_cnt)
        for index in range (0, p_cnt):
            pool_list.append (thread_pool.submit (start_fake_camera_simple, VIDEO_DICT['SOLID_BALL_001_P2'], '211'))
        for fu in as_completed (pool_list):
            res = fu.result ()
        return


def push_multi_sit_up():
    # start_fake_camera_simple(VIDEO_DICT['SIT_FORWARD_MULTI_001'], whole_rtsp='rtsp://192.168.2.235:8554/live401')
    # video = r"D:\99_TEST_VIDEO\CPP_Stress\02_multi_situp\101\2024_11_5_15_2_26_192.168.2.101_1_3_F_.mp4"
    # start_fake_camera_simple(video, )
    if ENV == 'Linux':
        video_path_dir = "/home/yskj/data/video/CPP_Stress/02_multi_situp"
    else:
        video_path_dir = r"D:\99_TEST_VIDEO\CPP_Stress\02_multi_situp"

    start_fake_camera_simple_dir(video_path_dir, whole_rtsp='rtsp://192.168.2.17:8554/live304')
    return

def push_solid_ball_video():
    start_fake_camera_simple(VIDEO_DICT['SOLID_BALL_STRESS_P1'], '161')
    start_fake_camera_simple(VIDEO_DICT['SOLID_BALL_STRESS_P2'], '211')
    return

def push_multi_solid_ball_video():
    rtsp_url_1 = 'rtsp://192.168.2.235:8554/live163'
    rtsp_url_2 = 'rtsp://192.168.2.235:8554/live164'
    rtsp_url_3 = 'rtsp://192.168.2.235:8554/live165'
    start_fake_camera_simple(VIDEO_DICT['SOLID_BALL_163'], whole_rtsp=rtsp_url_1)
    start_fake_camera_simple(VIDEO_DICT['SOLID_BALL_164'], whole_rtsp=rtsp_url_2)
    start_fake_camera_simple(VIDEO_DICT['SOLID_BALL_165'], whole_rtsp=rtsp_url_3)
    return

def push_50m_video():
    rtsp_url_1 = 'rtsp://192.168.2.235:8554/live600'
    rtsp_url_2 = 'rtsp://192.168.2.235:8554/live601'
    video_path_1 = "VIDEO_DICT['50M_001_START']"
    video_path_2 = "VIDEO_DICT['50M_001_OVER']"
    start_fake_camera_simple(eval(video_path_1), whole_rtsp=rtsp_url_1)
    start_fake_camera_simple(eval(video_path_2), whole_rtsp=rtsp_url_2)
    return

def push_800m_1000m_video():
    rtsp_url_1 = 'rtsp://192.168.2.235:8554/live70'
    rtsp_url_2 = 'rtsp://192.168.2.235:8554/live70/Streaming/Channels/3'
    rtsp_url_3 = 'rtsp://192.168.2.235:8554/live71'
    rtsp_url_4 = 'rtsp://192.168.2.235:8554/live71/Streaming/Channels/3'
    video_path_1 = "VIDEO_DICT['800_START_001']"
    video_path_2 = "VIDEO_DICT['800_START_001']"
    video_path_3 = "VIDEO_DICT['800_OVER_001']"
    video_path_4 = "VIDEO_DICT['800_OVER_SON_001']"

    start_fake_camera_simple(eval(video_path_1), whole_rtsp=rtsp_url_1)
    start_fake_camera_simple(eval(video_path_3), whole_rtsp=rtsp_url_3)
    start_fake_camera_simple(eval(video_path_4), whole_rtsp=rtsp_url_4)
    return

def push_multi_sit_forward():
    start_fake_camera_simple(VIDEO_DICT['SIT_FORWARD_MULTI_001'], whole_rtsp='rtsp://192.168.2.235:8554/live401')
    return

def push_volley_ball():
    start_fake_camera_simple(VIDEO_DICT['VOLLEY_BALL_001'], whole_rtsp='rtsp://192.168.2.235:8554/live11')
    return

def push_foot_ball():
    start_fake_camera_simple(VIDEO_DICT['FOOT_BALL_151'], whole_rtsp='rtsp://192.168.2.235:8554/live1201')
    start_fake_camera_simple (VIDEO_DICT['FOOT_BALL_152'], whole_rtsp='rtsp://192.168.2.235:8554/live1202')
    return

def push_basket_ball():
    start_fake_camera_simple(VIDEO_DICT['BASKET_BALL_START'], whole_rtsp='rtsp://192.168.2.235:8554/live1001')
    start_fake_camera_simple (VIDEO_DICT['BASKET_BALL_END'], whole_rtsp='rtsp://192.168.2.235:8554/live1002')
    return

def push_50_8():
    start_fake_camera_simple(VIDEO_DICT['50_MULTI_8_2_CAMRA_START'], whole_rtsp='rtsp://192.168.2.235:8554/live2104')
    start_fake_camera_simple (VIDEO_DICT['50_MULTI_8_2_CAMRA_OVER'], whole_rtsp='rtsp://192.168.2.235:8554/live2107')
    return

def push_sit_up():
    start_fake_camera_simple (VIDEO_DICT['SIT_UP_FACE_001'], whole_rtsp='rtsp://192.168.2.235:8554/live301')
    return

if __name__ == '__main__':
    # SIT_FORWARD_FOUL_002
    # MULTI_SIT_UP
    # start_fake_camera_simple(VIDEO_DICT['ROPE_SKIPPING_FACE_001'], '400')
    # rtsp_url_1 = 'rtsp://192.168.2.235:8554/live101'
    # start_fake_camera_simple(video, whole_rtsp=rtsp_url_1)
    # push_800m_1000m_video()
    # push_multi_sit_forward_video()
    # push_50m_video()
    # push_multi_sit_up()
    # push_multi_sit_forward()
    # push_multi_solid_ball_video()
    # push_volley_ball()
    # push_foot_ball()
    # push_basket_ball()
    # push_50_8()
    # push_sit_up()
    # push_multi_sit_up()
    push_multi_sit_forward_video()
    pass

