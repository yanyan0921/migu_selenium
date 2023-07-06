import redis_til
import time
import os


def get_results():
    files_path = os.getcwd() + "/" + 'results'
    success_times, fail_times, stop_session_success_times, stop_session_fail_times = 0, 0, 0, 0
    for file_name in os.listdir(files_path):
        current_file = files_path + '/' + file_name
        with open(current_file, 'r') as record_file:
            all_text = record_file.read()
            # 获取成功和失败所在下标
            success_index = all_text.find('Success Times')
            success_num = len('Success Times') + 2
            fail_index = all_text.find('Failed Times')
            fail_num = len('Failed Times') + 2

            stop_session_success_index = all_text.find('Stop Session Success Times')
            stop_session_success_num = len('Stop Session Success Times') + 2
            stop_session_fail_index = all_text.find('Stop Session Fail Times')
            stop_session_fail_num = len('Stop Session Fail Times') + 2

            # last_line = record_file.readlines()[2]
            # print("last_line=", last_line)
            # 获取成功失败次数，用strip()去掉多余空格
            success_times += int(all_text[success_index + success_num:fail_index].strip())
            # print(success_times)
            # print(fail_index + fail_num)
            # print(fail_index + fail_num + 5)
            # print(all_text[fail_index + fail_num:(fail_index + fail_num + 5)].strip())
            fail_times += int(all_text[fail_index + fail_num:stop_session_success_index].strip())
            stop_session_success_times += int(
                all_text[stop_session_success_index + stop_session_success_num:stop_session_fail_index].strip())
            stop_session_fail_times += int(all_text[stop_session_fail_index + stop_session_fail_num:(
                        stop_session_fail_index + stop_session_fail_num + 5)].strip())

    print('success_times:', success_times)
    print('fail_times:', fail_times)
    print('stop_session_success_times:', stop_session_success_times)
    print('stop_session_fail_times:', stop_session_fail_times)

    return success_times, fail_times
