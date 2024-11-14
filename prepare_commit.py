import os
import shutil
# from util import *

BASEDIR = os.path.dirname(__file__)
print(f'BASEDIR:{BASEDIR}')


def remove_cache(folder_path, dst_dir='cache__'):
    for root, dirs, files in os.walk(folder_path):
        # print (f"root: {root}")
        # print (f"dirs: {dirs}")
        for dir in dirs:
            if dst_dir in dir:
                dir_path = os.path.join(root, dir)
                shutil.rmtree(dir_path)
                print(f"del: {dir_path}")
    return


def file_walk():
    # 要遍历的文件夹路径
    folder_path = "your_folder_path"
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)

    return

def clean_dir(folder_path):
    if not os.path.exists(folder_path):
       return
    shutil.rmtree(folder_path)
    # os.mkdir(folder_path)

if __name__ == '__main__':
   remove_cache(BASEDIR, dst_dir='cache__')
   remove_cache(BASEDIR, dst_dir='report')
   remove_cache(BASEDIR, dst_dir='.pytest_cache')
   clean_dir(folder_path='../auto_test_log')
