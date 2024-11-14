# coding=utf-8

import yaml
import json
import os

def read_file_by_line(file_name: str) -> list:
    """
    读取文本用例数据
    :param file_name: 文件路径
    :return: list
    """
    with open (file_name, "r") as file:
        for line in file:
            print (line.strip ())
    return

def get_case_data_list(file_name: str) -> list:
    """
    读取文本用例数据
    :param file_name: 文件路径
    :return: list
    """
    with open(file_name, mode="r", encoding="utf-8") as f:
        data_list = f.readlines()
    data_list = [line.strip() for line in data_list]
    return data_list

def read_yaml_dict(file_name: str) -> dict:
    """
    读取文本用例数据
    :param file_name: 文件路径
    :return: list
    """
    data_dic = {}
    with open(file_name, 'r', encoding='utf-8') as wf:
        record_dic = yaml.safe_load(wf)
    return record_dic

def dump_file(file_name, data) -> int:
    """
    读取文本用例数据
    :param file_name: 文件路径
    :return: list
    """
    # file_name = os.path.join(file_path, file_name)

    yaml_support = True
    if yaml_support:
        with open(file_name, 'w', encoding='utf-8') as wf:
            yaml.safe_dump(data, wf, default_flow_style=False, allow_unicode=True)
    else:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    return 0

def dump_json(file_name: str, data: dict) -> int:
    """
    读取文本用例数据
    :param file_name: 文件路径
    :return: list
    """
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return 0

def read_json_dict(file_name: str) -> dict:
    """
    读取文本用例数据
    :param file_name: 文件路径
    :return: list
    """
    data_dic = {}
    with open(file_name, 'r') as wf:
        data_dic = json.load(wf)
    return data_dic

def read_file_str(file_name):
    """
    读取文本用例数据
    :param file_name: 文件路径
    :return: list
    """
    # 打开文件，返回一个文件对象
    with open(file_name, 'r', encoding='gbk') as file:
        # 读取文件的全部内容
        content = file.read ()
        # print(content)
    return content

sanity_result_file_map = {'we_chat': 'we_chat_result.yaml',
                          'face_mode': 'face_mode_result.yaml',
                          'free_mode': 'free_mode_result.yaml'}

project_foul_file_map = {"立定跳远": 'stand_jump_foul.yaml',
                        '引体向上': 'pull_up_foul.yaml',
                        '仰卧起坐': 'sit_up_foul.yaml',
                        '坐位体前屈': 'sit_forward_foul.yaml',
                        '跳绳': 'rope_skip_foul.yaml',
                        '50米': '50M_foul.yaml',
                        '实心球': 'solid_ball_foul.yaml',
                        '开机消息检测': 'message_detect.yaml',}

def update_result(path, dict_para, test_mode=None) -> None:
    test_mode = dict_para.get('test_mode', None)
    project_name = dict_para.get('project_name', None)
    print (f'project_name:{project_name}')
    test_result = dict_para.get('test_result', None)
    if not test_mode:
        raise ValueError (f"test_mode is None")
        # file = dict_para.get('file', 'free_mode_result.yaml')

    test_name = dict_para.get('test_name', None)
    # print (f'test_mode:{test_mode}')
    # foul test
    if test_name:
        file = project_foul_file_map.get(f'{project_name}', 'free_mode_result_foul.yaml')
    else:
        file = sanity_result_file_map.get (f'{test_mode}', None)

    if not file:
        raise ValueError (f"test_mode is None")

    print (f'file:{file}')
    file = os.path.join(path, file)

    target_dict = {}
    if os.path.exists(file):
        target_dict = read_yaml_dict(file)

    if test_name:
        target_dict.update ({f'{test_name}': f'{test_result}'})
    else:
        target_dict.update({f'{project_name}': f'{test_result}'})

    print(f'target_dict:{target_dict}')

    ret = dump_file(file, target_dict)
    # my_log.info(f'dump result:{ret}')
    return


def update_result_dir(path, dict_para) -> None:
    file = dict_para.get ('file', None)
    file = os.path.join (path, file)
    project_name = dict_para.get ('project_name', None)
    test_name = dict_para.get ('test_name', None)
    test_result = dict_para.get ('test_result', None)

    keep_result = {}
    target_dict = {}
    if os.path.exists (file):
        target_dict = read_yaml_dict(file)

    if test_name:
        if target_dict:
            target_dict.update({f'{test_name}': f'{test_result}'})
        else:
            target_dict = {f'{test_name}': f'{test_result}'}
    else:
        keep_result = {f'{project_name}': f'{test_result}'}
        target_dict.update(keep_result)

    print(f'target_dict:{target_dict}')

    ret = dump_file (file, target_dict)
    # my_log.info(f'dump result:{ret}')
    return


test_map_dict = {'class_list': 'class_list_sanity_map.yaml',
                'face_mode': 'face_mode_sanity_map.yaml',
                'free_mode': 'free_mode_sanity_map.yaml'}

def update_case_map(result_path, case_file, dict_para) -> None:
    project_name = dict_para.get('projectName', None)
    result_dic = dict_para.get('result_dic', None)
    test_mode = result_dic.get('test_mode', None)
    
    print (f'test_mode:{test_mode}')
    if test_mode:
        result_file = test_map_dict.get(f'{test_mode}', 'free_mode_sanity_map.yaml')
    else:
        raise ValueError (f"test_mode is None")

    result_file = os.path.join(result_path, result_file)
    result_dic = {}
    if os.path.exists(result_file):
        result_dic = read_yaml_dict(result_file)
    else:
        pass
    result_dic.update({f'{project_name}': f'{case_file}'})
    print(f'result_dic:{result_dic}')
    dump_file(result_file, result_dic)
    return

def wrtie_file(file_name, content) -> None:
    # 打开文件，如果文件不存在，会创建文件；'a' 表示追加模式，如果文件已存在，则会在文件末尾追加内容
    with open (file_name, 'a') as file:
        # 追加文本数据
        file.write(content)
    return

if __name__ == '__main__':
    data_dict = {"checkStyle":3,"clothesList":[{"colorCode":48,"colorNum":0,"studentId":"123"}],"errorCode":0,"foul_action":0,"key_image_1":"","key_image_2":"http://192.168.2.237:80/data/LongRunAutoFace/2024_11_13/2024_11_13_15_41_18_0_start.jpg","key_image_3":"http://192.168.2.237:80/data/LongRunAutoFace/2024_11_13/2024_11_13_15_44_59_123_over.jpg","locationId":64,"messageAck":0,"messageComment":"ScoreMessage","messageContentType":4,"messageCtrlType":1,"messageId":0,"messageScopeType":1,"metric_scores":[],"number":217.8800048828125,"projectType":7,"sceneType":7,"sendTime":1731483899411,"sonVideoUrl":"http://192.168.2.237:80/data/LongRunAutoFace/2024_11_13/2024_11_13_15_41_18_7_id_0_face_0__son.mp4","student_num":0,"taskContentId":3652,"track":0,"truthTaskContentId":3652,"video_url":"http://192.168.2.237:80/data/LongRunAutoFace/2024_11_13/2024_11_13_15_41_18_7_id_0_face_0_.mp4","workResult":0}
    file = r'D:/hello.yaml'
    dump_file(file, data_dict)