import main
from datetime import timedelta
import time
import datetime

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


def utc_to_kst(origin_time):  # UTC시간에서 KST로 변환해줌
    return (origin_time + timedelta(hours=9)).strftime("%Y-%m-%d %T")


def int_utc_to_kst(origin_time):  # UTC시간에서 KST로 변환해줌
    temp = (origin_time + timedelta(hours=9)).strftime("%Y-%m-%d %T")
    return datetime.datetime.strptime(temp, "%Y-%m-%d %H:%M:%S")


async def get_audit_log(guild, audit_type, member_id):
    async for entry in guild.audit_logs(action=audit_type, limit=1):
        log = entry
        logtime = int_utc_to_kst(log.created_at)
        logtime = int(time.mktime(logtime.timetuple()))
        runtime = datetime.datetime.now()
        runtime = int(time.mktime(runtime.timetuple()))
        if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
            return log.user.id
        else:
            return member_id

'''
async def get_audit_log(guild, audit_type):
    async for entry in guild.audit_logs(action=audit_type, limit=1):
        if entry.user is not None or entry.user is not False:
            return entry.user.id
        else:
            return "Unknown User"
'''
