import redis

from logger import logger as log


def init_User(UP_USER):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='nil', decode_responses=True)
    # UP_USER = ['lihongtao', 'jinqin']
    USER_LIST = 'UP_USER'
    # 删除现有用户数据
    r.delete(USER_LIST)
    for user in UP_USER:
        r.lpush(USER_LIST, str(user))
    all_users = r.lrange(USER_LIST, 0, -1)
    log.info(f'all users:{all_users}')


def get_User():
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='nil', decode_responses=True)
    USER_LIST = 'UP_USER'
    user_account = r.lpop(USER_LIST)
    if user_account == None:
        print('暂无用户可用')
    return user_account


def tested_users(table_name, tested_user):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='nil', decode_responses=True)
    r.lpush(table_name, str(tested_user))


def get_table_length(table_name):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='nil', decode_responses=True)
    list = r.lrange(table_name, 0, -1)
    length = len(list)
    return length


def delete_table(table_name):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='nil', decode_responses=True)
    r.delete(table_name)


def set_key(key_name, key_value):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='nil', decode_responses=True)
    r.set(key_name, key_value)


def get_value(key_name):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='nil', decode_responses=True)
    value = r.get(key_name)
    return value
