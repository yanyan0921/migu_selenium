import time
import redis
import gevent
import requests
import json
import hashlib
import datetime
import configparser
import redis_til
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from logger import logger as log
from selenium.webdriver.chrome.options import Options





class TestLoginAndStartGame():
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read('config.yaml')
        self.tested_users = 'TESTED_USER'
        self.test_status = 'ALREADY_TEST'
        # 在redis中获取用户，考虑若无用户情况！！
        self.user_account = redis_til.get_User()
        self.user_password = 'Unity@123'
        # 无页面启动
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # self.driver = webdriver.Chrome(options=chrome_options)
        self.driver = webdriver.Chrome()
        # configs
        # 平台URL
        self.base_url = "https://cloud-platform.migu.cn"
        # 等待游戏启动时间配置
        self.start_max_wait_time = 20000
        self.start_once_wait_time = 15
        # 等待video load 时间配置
        self.video_max_wait_time = 120
        self.video_once_wait_time = 15
        # todo: 第几个项目和调试APP中第几个APP
        self.project_index = 5
        # 需要对项目详情中第几列内容做出选择
        self.project_arrange = 8
        # 第几个App
        self.app_index = 2
        # todo: 改成测试用的orgId和appName
        self.orgId = "6434f8a8a420ac0020f1ec7f"
        self.appName = "青霄游戏-无remote包"
        # todo: 运行几次测试
        self.test_times = int(cf.get('TEST', 'test_times'))
        self.salt_data = None
        # 获取所有用户名单
        self.all_users = cf.get('UP_USER', 'user').split()


        # 点击 启动
        # self.start_button = '/html/body/div[1]/section/section/main/div[2]/div/div[2]/div/div/div[2]/div/div/button'
        self.start_button = '/html/body/div[1]/section/section/main/div[2]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div/div/button'
        # # 切换组织图标
        # self.org_logo = '/html/body/div[1]/section/header/section/div/div'
        # # 切换组织按钮
        # self.switch_org = '/html/body/div[2]/div[1]/div/div[1]/div/ul/li[1]/span'
        # # 组织切换至验收测试组
        # self.select_ystest = '/html/body/div[2]/div[2]/span[1]/ul[1]/li'
        # 点击 查看（ystest_perf_pub）
        self.query_test = '/html/body/div[1]/section/section/main/div[2]/div/div/div/div/div[2]/div[1]/div[3]/div/div[1]/div/table/tbody/tr[8]/td[5]/div/button[2]'

        # 点击 操作 图标
        self.operate_choose = '/html/body/div[1]/section/section/main/div[2]/div/div/div/div[2]/div/div/div[1]/div/div/div[2]/div[1]/div[3]/div/div[1]/div/table/tbody/tr[1]/td[7]/div/div'

        # 点击运行
        self.operate_start = '/html/body/div[2]/div[5]/div/div[1]/div/ul/li[1]'






    def login_and_start_game(self):
        # 输入账户、密码、验证码
        self.driver.get(self.base_url)
        self.driver.maximize_window()
        log.info(f'self.user_account={self.user_account}')
        self.driver.find_element(By.ID, "username").send_keys(self.user_account)
        self.driver.find_element(By.ID, "password").send_keys(self.user_password)
        self.driver.find_element(By.CSS_SELECTOR, ".el-input__clear > svg").click()
        self.driver.find_element(By.CSS_SELECTOR, ".el-input__clear > svg").click()
        self.driver.find_element(By.CSS_SELECTOR, ".el-input__suffix-inner .icon").click()
        self.driver.find_element(By.CSS_SELECTOR, ".\\_inlineLeft_180h3_28 .el-input__inner").click()
        code = self.get_verify_code()
        self.driver.find_element(By.CSS_SELECTOR, ".\\_inlineLeft_180h3_28 .el-input__inner").send_keys(code)
        # 点击登录
        self.driver.find_element(By.CSS_SELECTOR, ".el-button--primary").click()
        log.debug("log in")
        # 在关联unity界面点击：以后关联
        time.sleep(1)
        later_button = '/html/body/div/div/div[2]/div/form/div[3]/button'
        self.driver.find_element(By.XPATH, later_button).click()

        # 点击 项目管理
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".el-menu-item:nth-child(3)")))
        self.driver.find_element(By.CSS_SELECTOR, ".el-menu-item:nth-child(3)").click()

        # 点击 查看test项目
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, self.query_test)))
        self.driver.find_element(By.XPATH, self.query_test).click()


        # 获取当前窗口
        current_handler = self.driver.current_window_handle
        success_times = 0
        fail_times = 0
        stop_session_success_times = 0
        stop_session_fail_times = 0
        run_times = self.test_times
        # result_file_name = f"result_{time.time()}.log"
        result_file_name = f"result_{self.user_account}_{time.time()}.log"
        file_path = os.getcwd() + "/" + 'results' + '/' + result_file_name
        with open(file_path, 'a+') as record_file:
            for i in range(run_times):
                log.info(f'开启第{i + 1}轮压测')
                start_time = str(datetime.datetime.now())
                log.info(f"{self.user_account},timestamp: {start_time} try to start new app")
                run_status = self.start_game(current_handler)
                record_file.writelines([f"Time:{start_time} Success={str(run_status)}\n"])

                if run_status is True:
                    success_times += 1
                else:
                    fail_times += 1
                log.info(f"{success_times=} {fail_times=}")

                # 将该用户放入redis表中
                redis_til.tested_users(self.tested_users, self.user_account)
                # 同步redis，该用户已完成一轮压测
                log.info(f'用户{self.user_account}已完成第{i+1}轮压测，等待其他用户')
                # 计算该表是否已满用户，若用户已满，删除表格，停止目前正在运行的服务器
                # 并且：将redis中alrea_test键设为1，表明此时可进行下一轮压测
                test_status = redis_til.get_value(self.test_status)
                log.info(f'当前可压测状态为：{test_status}')
                while not int(test_status):
                    table_length = redis_til.get_table_length(self.tested_users)
                    log.info(f'当前已完成压测用户数量为{table_length}')
                    if table_length == len(self.all_users):
                        redis_til.delete_table(self.tested_users)
                        stop_session_result = self.stop_user_tasks()
                        log.info(f'停止所有服务器结果为：{stop_session_result}')
                        record_file.writelines([f"Time:{start_time} stop_session_result={stop_session_result}\n"])
                        if stop_session_result == "success":
                            stop_session_success_times += 1
                        if stop_session_result == "fail":
                            stop_session_fail_times += 1
                        redis_til.set_key(self.test_status, 1)
                        log.info('将test_status设为1')
                    time.sleep(10)
                    test_status = redis_til.get_value(self.test_status)
                    log.info(f'此时test_status状态为:{test_status}')
                time.sleep(15)
                redis_til.set_key(self.test_status, 0)
                gevent.sleep(10)
            record_file.writelines([f"Success Times: {success_times} Failed Times: {fail_times} Stop Session Success "
                                    f"Times: {stop_session_success_times} Stop Session Fail Times: {stop_session_fail_times}     \n"])
        log.info("end of test...")


    def start_game(self, current_handler):
        success = None
        time.sleep(5)
        try:
            # 点击ystest_xxxx_start_game的操作图标
            WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.XPATH, self.operate_choose)))
            self.driver.find_element(By.XPATH, self.operate_choose).click()
        except:
            log.info('未找到游戏的操作图标')
            pass
        # 点击运行
        time.sleep(5)
        WebDriverWait(self.driver, 20).until(
            expected_conditions.presence_of_element_located((By.XPATH, self.operate_start)))
        self.driver.find_element(By.XPATH, self.operate_start).click()
        time.sleep(5)

        # 点击 启动
        time.sleep(1)
        self.driver.find_element(By.XPATH, self.start_button).click()

        # 等待window启动，并切换到新window
        wait_time = 0
        once_wait_time = self.start_once_wait_time
        # 等待超时时长
        max_wait_time = self.start_max_wait_time

        while len(self.driver.window_handles) == 1:
            time.sleep(once_wait_time)
            wait_time += once_wait_time

            if wait_time > max_wait_time:
                log.info(f"waited too long time for new window: {wait_time=}")
                success = False
                break
            else:
                log.info(f"{self.user_account},waited {wait_time=} seconds for new window")

        if success is False:
            self.driver.refresh()
            return success

        for handler in self.driver.window_handles:
            if handler != current_handler:
                self.driver.switch_to.window(handler)
                break

        # 点击黑框启动icon来启动游戏
        time.sleep(3)
        start_game = 'el-icon'
        self.driver.find_element(By.CLASS_NAME,start_game).click()

        # 找到video element，等待其运行
        video_element = self.driver.find_element(By.ID, 'cursor-overlay')

        v_wait_time = 0
        v_once_wait_time = self.video_once_wait_time
        # 等待video元素运行，超时时长如下
        v_max_wait_time = self.video_max_wait_time

        is_active = False
        while is_active is False:
            time.sleep(v_once_wait_time)
            v_wait_time += v_once_wait_time
            if v_wait_time >= v_max_wait_time:
                log.info(f"video wait for running to long, failed: {v_wait_time=}")
                success = False
            try:
                # 出现视频流后，页面中video_element元素会出现style部件
                is_active = video_element.get_property('style')
                log.info(f"if style is active:{is_active}")
            except Exception as e:
                log.info(f"{e=}")
                is_active = False
            log.info(f"video running state: {is_active=}")

        if success is None:
            success = True

        log.info(f"video running state: {is_active=} {success=}")

        # 关闭当前窗口
        self.driver.close()
        self.driver.switch_to.window(current_handler)

        # 关闭服务器
        # stop running session
        # self.stop_user_tasks()
        return success

    def stop_user_tasks(self):
        cookies = self.driver.get_cookies()
        requests_cookies = {}
        for cookie in cookies:
            requests_cookies[cookie['name']] = cookie['value']

        # 1. query running tasks by orgId and Name
        running_tasks = self.query_running_tasks(requests_cookies)
        stop_result = "no_task"
        if running_tasks is not None and len(running_tasks) > 0:
            for task in running_tasks:
                appRunId = task.get("appRunId")
                stop_result = self.stop_game_session(appRunId, requests_cookies)

        return stop_result

    def stop_game_session(self, run_id, requests_cookies):
        api_url = f"/api/stop-game-session/{run_id}"
        x_t = self.get_timestamp_millisecond()
        x_st = self.get_salt(cookies=requests_cookies)
        x_sn = self.get_signature(api_url, None, None, x_t, x_st)
        headers = self.set_request_header_no_type(x_t, x_sn, x_st)
        r = self.send_requests('POST', self.base_url + api_url, req_body=None, req_headers=headers,
                               req_cookies=requests_cookies)
        body = r.json()
        if r.status_code != 200 or body.get("message") != "success":
            log.info(f"stop session {run_id} failed")
            return "fail"
        else:
            log.info(f"stop session {run_id} success")
            # 将关闭进程成功写进文档中
            return "success"

    def query_running_tasks(self, requests_cookies):
        # 查询当前是否有app正在运行
        # 单个用户不执行关闭操作，一轮用户完成后统一关闭，并记录关闭成功数量
        api_url = "/api/process/appRun/filter"
        querystring = "page=1&pageSize=10"

        req_body = {
            "appRunStatuses": [],
            "orgId": "",
            "appName": self.appName,
            "appEnv": "",
            "durationSort": 0,
            "regionIds": [],
            "appRunStopCauses": []
        }

        x_t = self.get_timestamp_millisecond()
        x_st = self.get_salt(cookies=requests_cookies)
        x_sn = self.get_signature(api_url, querystring, json.dumps(req_body), x_t, x_st)
        headers = self.set_request_header(x_t, x_sn, x_st)
        url = self.base_url + api_url + "?" + querystring

        r = self.send_requests('POST', url, req_body=req_body, req_headers=headers, req_cookies=requests_cookies)
        body = r.json()
        if r.status_code != 200 or body.get("message") != "success":
            log.info("query running tasks failed")
            return None

        tasks = body.get("body").get("list")
        if tasks is None or len(tasks) == 0:
            log.info("query no running tasks")
            return None

        running_tasks = []
        for task in tasks:
            if task.get("appRunStatus") == "running":
                running_tasks.append(task)
        return running_tasks


    # 以下为请求migu所需util funcs
    def get_salt(self, cookies):
        # 不可以过于频繁请求salt
        if self.salt_data is None:
            url = self.base_url + "/api/dynamicSalt"
            r = requests.get(url, cookies=cookies)
            body = r.json().get("body")
            salt = body.get("salt")

            if salt is not None:
                self.salt_data = salt

        return self.salt_data

    @staticmethod
    def get_timestamp_millisecond():
        time_stamp = time.time()
        return int(round(time_stamp * 1000))

    @staticmethod
    def get_signature(api_url, query_string, req_body, timestamp, dynamic_salt):
        md5_str = api_url
        if query_string is not None:
            md5_str = md5_str + query_string
        if req_body is not None:
            md5_str = md5_str + req_body
        md5_str = md5_str + str(timestamp) + dynamic_salt
        hl = hashlib.md5()
        hl.update(md5_str.encode())
        return hl.hexdigest()

    @staticmethod
    def set_request_header(x_t, x_sn, x_st):
        return {
            'Content-Type': 'application/json',
            'X-T': str(x_t),
            'X-SN': x_sn,
            'X-ST': x_st
        }

    @staticmethod
    def set_request_header_no_type(x_t, x_sn, x_st):
        return {
            'X-T': str(x_t),
            'X-SN': x_sn,
            'X-ST': x_st
        }

    @staticmethod
    def send_requests(req_method, server_url, req_body, req_headers, req_cookies):
        response = ''
        if req_method == 'POST':
            response = requests.post(server_url, json=req_body, headers=req_headers, cookies=req_cookies)
        elif req_method == 'GET':
            response = requests.get(server_url, json=req_body, headers=req_headers, cookies=req_cookies)
        elif req_method == 'PUT':
            response = requests.put(server_url, json=req_body, headers=req_headers, cookies=req_cookies)
        elif req_method == 'PATCH':
            response = requests.patch(server_url, json=req_body, headers=req_headers, cookies=req_cookies)
        elif req_method == 'DELETE':
            response = requests.delete(server_url, json=req_body, headers=req_headers, cookies=req_cookies)
        log.debug('response status code is: ' + str(response.status_code))
        try:
            log.debug('Response body: ' + str(response.json()))
        finally:
            return response

    def get_verify_code(self):
        cookie_vs = self.driver.get_cookie("VS").get("value")
        url = self.base_url + "/api/test/verifyCode"
        payload = ""
        headers = {
          'Content-Type': 'application/json',
          'Cookie': f'VS={cookie_vs}'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        resp = response.json()
        code = resp.get("body")
        return code



