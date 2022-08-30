import main
from datetime import timedelta
channel_id = main.channel_id


def get_current_log_channel_id():
    """
    설정된 로그 채널 ID를 가져옵니다.
    :return: 로그 채널 ID (int)
    """
    return channel_id


def set_log_channel(cid: int):
    """
    로그 채널을 설정합니다.
    :param cid: 대상의 채널 ID (int)
    """
    global channel_id
    channel_id = cid

def utc_to_kst(origin_time):
    return (origin_time + timedelta(hours=9)).strftime("%Y-%m-%d %T")