# coding=utf-8

import os
import sys
import json
import time

from common.mylogger import my_log
from common.rtsp import *
import readFile
from component.mysql import Mysql
from common.contants import *


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


# 设置Chrome WebDriver
driver = webdriver.Chrome()

# 打开目标网站
driver.get("http://192.168.2.237/#/login")

# 找到用户名和密码的输入框
username_box = driver.find_elements(By.CLASS_NAME, "el-input__inner")[0]  # 假设用户名输入框的ID是'username'
print(f'username_box:{username_box}')
password_box = driver.find_elements(By.CLASS_NAME, "el-input__inner")[1]  # 假设密码输入框的ID是'password'
print(f'password_box:{password_box}')

# 输入用户名和密码
username_box.send_keys(f'{USER}')
password_box.send_keys(f'{PWD}')

# 找到登录按钮并点击
login_button = driver.find_element(By.CLASS_NAME, "el-button.el-button--primary.el-button--default.w100")
print(f'login_button:{login_button}')
login_button.click()

time.sleep(1)

# 考试模式
test_button = driver.find_elements(By.CLASS_NAME, "cur-p.test")[0]
print(f'test_button:{test_button}')
test_button.click()

time.sleep(1)

test_button = driver.find_elements(By.CLASS_NAME, "flex.ai-c.jc-c.new-task-type-btn.bg03c15e")[0]
print(f'test_button:{test_button}')
test_button.click()

time.sleep(60)

# 等待页面加载完成或者进行其他操作

# 关闭WebDriver
driver.quit()

# test_webpage("http://192.168.2.237/#/login")