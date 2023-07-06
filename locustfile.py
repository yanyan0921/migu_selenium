import sys

from locust import HttpUser, task
import time
import os
import queue
import requests
import test_locust
import redis
import result


# 我们在做接口自动化测试时，使用的是request对接口发起请求，在这里我们用的是locust中的httpuser对接口进行发起请求
class UserBehaviour(HttpUser):
    def on_start(self):
        print("准备启动游戏")

    def on_stop(self):
        print("准备停止游戏")
        # sys.exit()

    # def init_users(self):
    #     # 在redis中获取用户

    def login_and_start(self):
        print('登录')
        test_locust.TestLoginAndStartGame().login_and_start_game()

    def stop_game(self):
        print('关闭游戏')

    @task
    def test(self):
        # self.init_users()
        self.login_and_start()
        self.stop_game()
        # result.get_results()
        self.stop()

        # self.environment.runner.stop()


if __name__ == '__main__':
    pass
