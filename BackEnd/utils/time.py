# coding: utf-8
import functools
import random
import time
from datetime import datetime, timedelta
from logging import getLogger

import pytz

logger = getLogger(__name__)

PER_HOUR_SECONDS = 3600
PER_DAY_SECONDS = 24 * 3600
EAST_8_ZONE_SECONDS = 8 * 3600


def formatted_time_list(start_time, end_time=None, form='%Y-%m-%d'):
    """
    给出两个时间戳之间所有的格式化的时间，左闭右开
    :param start_time:起始时间，不能为空
    :param end_time:结束时间，可为空，若为空则做格式转换
    :param form: 默认格式是'%Y-%m-%d'
    :return:总是list，元素为string
    """
    if end_time is None:
        return to_formatted_time(start_time, form)
    start_time = datetime.fromtimestamp(int(start_time),
                                        tz=pytz.timezone('Asia/Shanghai'))
    end_time = datetime.fromtimestamp(int(end_time),
                                      tz=pytz.timezone('Asia/Shanghai'))
    date_list = []
    while start_time < end_time:
        date_list.append(start_time.strftime(form))  # 日期存入列表
        start_time += timedelta(days=+1)  # 日期加一天
    return date_list


def day_begin(t=None):
    """
    返回给定时间的凌晨0点的时间戳，注意，这里返回的是北京时间
    :param t: 时间戳，int/float/str都可
    :return: int型时间戳
    """
    if t is None:
        t = time.time()
    return ((int(t) + EAST_8_ZONE_SECONDS) //
            PER_DAY_SECONDS) * PER_DAY_SECONDS - EAST_8_ZONE_SECONDS


def day_end(t=None):
    """
    返回给定时间的24点（第二天的0点）的时间戳
    :param t: 时间戳，int/float/str都可
    :return: int型时间戳
    """
    return day_begin(t) + PER_DAY_SECONDS


def int_timestamp():
    """
    返回现在的int型的时间戳
    :return: 返回现在的int型的时间戳
    """
    return int(time.time())


def compare_date(time1, time2, form='%Y-%m-%d'):
    """
    给出两个时间，比较大小
    :param time1: 一个时间
    :param time2: 两个时间
    :param form: 时间的格式，方便做格式转换
    :return: time1?time2，大于1， 小于-1， 等于0
    """
    time1 = time.mktime(time.strptime(time1, form))
    time2 = time.mktime(time.strptime(time2, form))
    if time1 > time2:
        return 1
    elif time1 < time2:
        return -1
    else:
        return 0


def to_int_timestamp(t, form='%Y-%m-%d'):
    """
    给一个格式化的时间，返回其int型时间戳
    :param t: 格式化的时间（str）
    :param form: 时间的格式，默认为 %Y-%m-%d
    :return: int型时间戳
    """
    return int(time.mktime(time.strptime(t, form)))


def to_formatted_time(t=None, form='%Y-%m-%d'):
    """
    给出时间戳，返回格式化的时间
    :param t: 时间戳，int/float/str都可
    :param form: 期望的时间格式
    :return: 格式化的时间（str）
    """
    return datetime.fromtimestamp(int(t),
                                  tz=pytz.timezone('Asia/Shanghai')).strftime(form)


def month_day_count(month):
    """获得当年指定月份的天数"""
    date = datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    date.replace(month=month)
    if month == 12:
        next_month_first_date = datetime(date.year + 1, 1, 1)
    else:
        next_month_first_date = datetime(date.year, date.month + 1, 1)
    return (next_month_first_date - timedelta(1)).day


def seconds_to_tomorrow_end(random_: bool = False):
    """  获得到明天24点的秒数，可以设置一些随机数来避免一大堆数据同时过期  """
    now = int_timestamp()
    tom = day_end() + PER_DAY_SECONDS
    last = tom - now
    if random_:
        last += random.randint(-1 * PER_HOUR_SECONDS, PER_HOUR_SECONDS)
    return last


def randon_on_time():
    t = int_timestamp()
    t = (t - 1585114552) * 100 + random.randint(1, 99)
    return t


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print_args = str(args) + str(kwargs)
        print_args = print_args[:100] + '...' if len(
            print_args) > 100 else print_args
        logger.info(
            f'func {func.__name__} cost {end - start} seconds, args & kwargs: {print_args}'
        )
        return result
    
    return wrapper


if __name__ == '__main__':
    print("to_int_timestamp('2019-7-31')\n", to_int_timestamp('2019-7-31'))
    print("to_int_timestamp('2019.7.31', '%Y.%m.%d')\n",
          to_int_timestamp('2019.7.31', '%Y.%m.%d'))
    print("compare_date('2019-7-20', '2019-7-31')\n",
          compare_date('2019-7-20', '2019-7-31'))
    print("compare_date('2019.7.31', '2019.7.31', '%Y.%m.%d')\n",
          compare_date('2019.7.31', '2019.7.31', '%Y.%m.%d'))
    print("compare_date('2019-7-20', '2019-7-10', '%Y.%m.%d')\n",
          compare_date('2019-7-20', '2019-7-10', '%Y-%m-%d'))
    print("formatted_time_list('1564538424', '1564797624', '%Y-%m-%d')\n", \
          formatted_time_list('1564538424', '1564797624', '%Y-%m-%d'))
    print("formatted_time_list('1564538424', '1564797624', '%Y.%m.%d')\n", \
          formatted_time_list('1564538424', '1564797624', '%Y.%m.%d'))
