import logging
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests
from apscheduler.schedulers.blocking import BlockingScheduler

from log_config import init_log_config

init_log_config()

app_logger = logging.getLogger('badminton.' + __name__)

auth = 'IKS0rOIAz1EjWhKgv_8WGnzL6NJnnjqTKDKLfcqwNES7kzFFzIGEVx6HbE0-09J5'

yard_map = {
    1: 21,
    2: 22,
}
# 线程池
pool = ThreadPoolExecutor(max_workers=100)
tasks = [
    {
        "name": "小丁",
        "token": "IKS0rOIAz1EjWhKgv_8WGnzL6NJnnjqTKDKLfcqwNES7kzFFzIGEVx6HbE0-09J5",
        "yardIndex": 1,
        "times": [
            {
                "start": "13:30",
                "end": "15:00",
                "sessionId": None,
            },
            {
                "start": "15:00",
                "end": "16:45",
                "sessionId": None,
            }
        ],
        "dayOfWeek": 7,
        "enable": True
    },
    {
        "name": "小丁小号",
        "token": "kcjzYBka4eTwsMTAgq6Mgvf2wrvPoERbcNlp7jT4cWLYfViJt4xhH2CTiUA8PeVg",
        "yardIndex": 2,
        "times": [
            {
                "start": "13:30",
                "end": "15:00",
                "sessionId": None,
            },
            {
                "start": "15:00",
                "end": "16:45",
                "sessionId": None,
            }
        ],
        "dayOfWeek": 7,
        "enable": True
    },
    {
        "name": "小梁",
        "token": "lat51iC5ek_jm2B6sEz6qGYEhZv-xayRmAIF_XwQbEGvS-HmVqCE9CUZw4pZgBU9",
        "yardIndex": 1,
        "times": [
            {
                "start": "18:00",
                "end": "19:30",
                "sessionId": None,
            },
            {
                "start": "19:30",
                "end": "20:45",
                "sessionId": None,
            }
        ],
        "dayOfWeek": 6,
        "enable": True
    },
    {
        "name": "小梁小号",
        "token": "FbvLLgHfZXFZPlZs56vMcKy4xiufHR11ZjrEPDispSmEAKuNUR1NsUhCiM_u3m5J",
        "yardIndex": 2,
        "times": [
            {
                "start": "18:00",
                "end": "19:30",
                "sessionId": None,
            },
            {
                "start": "19:30",
                "end": "20:45",
                "sessionId": None,
            }
        ],
        "dayOfWeek": 6,
        "enable": True
    }
]

current_tasks = list()

def get_yard_info(yard_index):
    """
    获取场地信息
    :param yard_index: 场地一：1 场地二：2
    :return:
    """

    yard_id = yard_map.get(yard_index)
    app_logger.info(f'获取场次 {yard_index} 信息-开始')
    url = 'https://3rd.bluexii.cn/town-165/town/app/field/sign/get'
    headers = {
        'Authorization': auth,
    }
    json_payload = {
        'YardId': yard_id
    }
    response = requests.post(
        url=url,
        headers=headers,
        json=json_payload
    )
    res = response.json()
    data = res.get('Data')
    app_logger.info(f'获取场次 {yard_index} 信息-结束')
    return data


def update_task_info(multiple):
    global tasks
    global current_tasks
    yard_1_data = get_yard_info(1)
    yard_2_data = get_yard_info(2)

    yard_data = {**yard_1_data, **yard_2_data}

    for task in tasks:
        times = task.get('times')
        for play_time in times:
            for key, value in yard_data.items():
                yard_info = value.get('Info')
                yard_id = yard_map.get(task.get('yardIndex'))
                if yard_info.get('YardId') == yard_id and yard_info.get('Weekday') == task.get('dayOfWeek') and yard_info.get('StartDate') == play_time.get('start') and yard_info.get('EndDate') == play_time.get('end'):
                    play_time['sessionId'] = yard_info.get('Id')

    # 将每个任务都进行复制，后面并发请求
    current_tasks = tasks * multiple


def sign_yard(task_info):
    """
    :param task_info: 任务信息
    :return:
    """

    username = task_info.get('name')
    if not task_info.get('enable'):
        app_logger.warning(f'{username} enable = False 跳过预约')
        return

    app_logger.info(f'{username} 预约-开始，task info: {task_info}')
    url = 'https://3rd.bluexii.cn/town-165/town/app/field/sign'
    headers = {
        'Authorization': task_info.get('token'),
    }
    week_day = task_info.get('dayOfWeek')

    json_payload = {
        'SessionId': task_info.get('sessionId'),
        'FieldId': 21,
        'YardId': yard_map.get(task_info.get('yardIndex')),
        'StartDate': week_day_offset(week_day, task_info.get('startTime')),
        'EndDate': week_day_offset(week_day, task_info.get('endTime')),
        'UserName': '阿辉',
        'AppointmentNum': 8,
        'UserContact': '13173611581',
        'Remark': '打球',
        'IsSign': 1
    }
    response = requests.post(
        url=url,
        headers=headers,
        json=json_payload
    )
    res = response.json()
    app_logger.info(f'{username} 预约结果: {res}')
    app_logger.info(f'{username} 预约-结束')
    return res


def week_day_offset(weekday, time_str):
    """
    返回星期 n 的日期
    :param weekday: 1-7 表示星期几
    :param time_str: 时间部分，字符串，格式：11:30
    :return: 当天所处星期的星期 n 的日期
    """

    today = datetime.today()
    current_weekday = today.isoweekday()  # 获取当前是周几 (1=周一, 7=周日)
    delta_days = weekday - current_weekday  # 计算目标日期的偏移量

    target_date = today + timedelta(days=delta_days)

    # 解析时间字符串
    hours, minutes = map(int, time_str.split(":"))

    # 替换时间部分
    target_datetime = target_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)

    # 格式化为字符串 "yyyy-MM-dd HH:mm:ss"
    return target_datetime.strftime("%Y-%m-%d %H:%M:%S")


def order_task():
    cnt = 1
    for task in current_tasks:
        times = task.get('times')
        for play_time in times:
            task_info = {
                'sessionId': play_time.get('sessionId'),
                'token': task.get('token'),
                'yardIndex': task.get('yardIndex'),
                'dayOfWeek': task.get('dayOfWeek'),
                'enable': task.get('enable'),
                'startTime': play_time.get('start'),
                'endTime': play_time.get('end'),
            }
            print(f'预定: {cnt}')
            sign_yard(task_info)
            cnt += 1


def multi_thread_order():
    app_logger.info(f'开始执行任务, 原始任务数量: {len(tasks)}, 待执行任务总数: {len(current_tasks)}')
    for task in current_tasks:
        times = task.get('times')
        for play_time in times:
            task_info = {
                'name': task.get('name'),
                'sessionId': play_time.get('sessionId'),
                'token': task.get('token'),
                'yardIndex': task.get('yardIndex'),
                'dayOfWeek': task.get('dayOfWeek'),
                'enable': task.get('enable'),
                'startTime': play_time.get('start'),
                'endTime': play_time.get('end'),
            }
            pool.submit(sign_yard, task_info)


def main():

    # 创建 BlockingScheduler 实例
    scheduler = BlockingScheduler()
    # 添加定时任务
    scheduler.add_job(update_task_info, 'cron', hour=8, minute=25, second=0, args=(20,))
    scheduler.add_job(multi_thread_order, 'cron', hour=8, minute=30, second=0)

    app_logger.info("任务调度器启动...")
    scheduler.start()


if __name__ == '__main__':
    main()
