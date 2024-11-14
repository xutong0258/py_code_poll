# coding=utf-8
import os
import re
import platform


ENV = platform.system()
print(f'ENV:{ENV}')

SEP = r'\\'
if ENV == 'Linux':
    VIDEO_PATH = r'/home/yskj/data/video'
else:
    VIDEO_PATH = r'D:/99_TEST_VIDEO'

VIDEO_DICT = dict()

def add_video_path(key, simple_path):
    path = os.path.join(VIDEO_PATH, simple_path)
    VIDEO_DICT.update({key: path})
    return

def prepare_video_path():
    if ENV == 'Windows':
        # print(f'in Windows')
        for key, value in VIDEO_DICT.items():
            VIDEO_DICT[key] = value.replace('/', '\\')
            # print(f'item:{VIDEO_DICT[key]}')
    return

if __name__ == '__main__':
    pass