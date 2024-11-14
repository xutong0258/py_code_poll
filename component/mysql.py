# coding=utf-8

import pymysql
import time
import datetime

from common.contants import *

from common.mylogger import my_log

mysql_dict = ENV_DICT.get('mysql', None)

class Mysql:

    def __init__(self):
        # 连接到数据库
        self.con = pymysql.connect(
                                    host=eval(mysql_dict.get("host")),
                                    user=mysql_dict.get("user"),
                                    password=mysql_dict.get("password"),
                                    port=int(mysql_dict.get("port")),
                                    db=mysql_dict.get("db"),
                                    charset="utf8")
        # 创建一个游标
        self.cur = self.con.cursor()
        my_log.info(f"DB OK self.cur:{self.cur}")
        return


    def get_one(self, sql):
        """获取查询到的第一条数据"""
        self.con.commit()
        self.cur.execute(sql)
        return self.cur.fetchone()

    def get_all(self, sql):
        """获取sql语句查询到的所有数据"""
        self.con.commit()
        self.cur.execute(sql)
        return self.cur.fetchall()

    def count(self, sql):
        """获取sql语句查询到的所有数据"""
        self.con.commit()
        res = self.cur.execute(sql)
        return res

    def close(self):
        # 关闭游标对象
        self.cur.close()
        # 断开连接
        self.con.close()

    def update(self, sql):
        """获取sql语句查询到的所有数据"""
        self.cur.execute(sql)
        self.con.commit()
        return

    def disable_all_project(self):
        """获取sql语句查询到的所有数据"""
        # my_log.info(f'proj_name:{proj_name}')

        sql = f"UPDATE se.project SET is_disabled = 1 WHERE name != '阳光跑' "
        self.cur.execute(sql)

        sql = f"UPDATE se.free_mode SET is_disabled = 1"
        self.cur.execute (sql)

        self.con.commit()
        return


    def enable_all_project(self):
        """获取sql语句查询到的所有数据"""
        # my_log.info(f'proj_name:{proj_name}')

        sql = f"UPDATE se.project SET is_disabled = 0"
        self.cur.execute(sql)
        self.con.commit()
        return

    def set_test_project_db(self, proj_name, is_disabled=0, is_free_mode=False):
        """获取sql语句查询到的所有数据"""
        if '多人' in proj_name:
            proj_name = proj_name.replace ('多人', '')
        if '计圈跑' in proj_name:
            proj_name = '计圈跑'
        if '定距跑' in proj_name:
            proj_name = '定距跑'
        my_log.info(f'proj_name:{proj_name}')

        sql = f"UPDATE se.project SET is_disabled = {is_disabled} WHERE name = '{proj_name}'"
        self.cur.execute(sql)

        if is_free_mode:
            sql = f"UPDATE se.free_mode SET is_disabled = {is_disabled} WHERE project_name = '{proj_name}'"
            self.cur.execute(sql)

        self.con.commit()
        return


    def get_student_num(self):
        """获取sql语句查询到的所有数据"""
        sql = f"SELECT num from se.student"
        res = self.get_all(sql)
        student_num = res[-1]
        my_log.info(f'student number:{res[-1]}')
        # classId = res[-1][0]
        # my_log.info(f'get_class_id:{classId}')
        return student_num

    def insert_rec(self, append_dic):
        """获取sql语句查询到的所有数据"""
        sql_header = 'INSERT INTO se.auto_test(test_item, test_result, test_mode, test_time, test_env) \n'
        test_item = append_dic['test_item']
        test_result = append_dic['test_result']
        test_mode = append_dic['test_mode']
        test_time = append_dic['test_time']
        # test_env = append_dic['test_env']
        # tester = append_dic['tester']

        sql_value = f"VALUES('{test_item}', '{test_result}', '{test_mode}', '{test_time}', '{TEST_SERVER}');"

        sql = sql_header + sql_value
        my_log.info(f'sql:{sql}')

        self.cur.execute(sql)
        self.con.commit()
        return


    def update_sql(self, sql_list):
        for item in sql_list:
            my_log.info(f'sql item:{item}')
            self.update(item)
            # time.sleep(5)
        return

if __name__ == '__main__':
    db = Mysql()
    db.disable_all_project()
    # db.enable_all_project()

    if current_enable:
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        append_dic = {"test_item": "stand_jump",
                      "test_result": "PASS",
                      "test_mode": "class_list",
                      "test_time": time_stamp,
                      "test_env": "201",
                      "tester": "stone"}

        db.insert_rec(append_dic)