import configparser
import os
import time

import redis_til
from redis_til import init_User
from logger import logger as log
from test_locust import TestLoginAndStartGame
from result import get_results

if __name__ == '__main__':
    #  实例化configParser对象
    cf = configparser.ConfigParser()
    cf.read('config.yaml')
    # 1、初始化用户
    UP_USER = cf.get('UP_USER', 'user')
    UP_USER = UP_USER.split()
    log.info(f"本轮所使用的压测用户为={UP_USER}")
    init_User(UP_USER)
    # 删除已完成压测用户数量表
    redis_til.delete_table('TESTED_USER')
    # 2、启动locust，无界面启动，设定并发数量用户
    os.system("locust -f locustfile.py --host=127.0.0.1 --headless -u 4 -r 1")
    print("压测已完成")

# 3、等待所有用户加载游戏成功/失败后，停止所有游戏进程，统计停止游戏的成功次数，完成一轮后，继续下一轮
# 6、避免locust多次重复启动（只能用一个用户重复启动使用）
