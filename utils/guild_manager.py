"""
    #제작: @17th, @donggeon
    #최종 수정일: 2022년 09월 02일
"""

import main
from datetime import timedelta
import time
import datetime

channel_id = main.LOG_CHANNEL_ID


def get_current_log_channel_id(gid: int):
    """
    길드에 설정된 로그 채널 ID를 가져옵니다.
    :return: 로그 채널 ID (int)
    """
    for cid in channel_id:
        if cid == "{0}:{1}".format(str(gid), cid[cid.index(":") + 1:]):
            return int(cid[cid.index(":") + 1:])
    return None


def is_guild_registered(gid: int):
    for cid in channel_id:
        if cid.startswith(str(gid)):
            return True
    return False


def set_log_channel(gid: int, cid: int, isready: bool = False):
    """
    로그 채널을 설정합니다.
    :param gid: 바꿀 길드 ID
    :param cid: 대상의 채널 ID (int)
    :param isready: 준비 단계 인가요?
    """
    if isready:
        channel_id.append("{0}:{1}".format(gid, cid))
    else:
        if get_current_log_channel_id(gid) is None:
            channel_id.append("{0}:{1}".format(gid, cid))
            with open("./setting.txt", 'a') as setting_file:
                setting_file.write("{0}:{1}\n".format(gid, cid))
        else:
            before = get_current_log_channel_id(gid)
            channel_id.remove("{0}:{1}".format(gid, before))
            channel_id.append("{0}:{1}".format(gid, cid))
            with open("./setting.txt", 'r') as setting_read:
                origin = ""
                for setting in setting_read.readlines():
                    origin += "{0}".format(setting.replace(str(before), str(cid)))
                with open("./setting.txt", 'w') as setting_file:
                    setting_file.truncate(0)
                    setting_file.write(origin)


def get_all_log_channel():
    setting_file = open("./setting.txt", 'r')
    _temp = []
    for value in setting_file:
        _temp.append("{0}:{1}".format(int(value[:value.index(":")]), int(value[value.index(":")+1:])))
    return _temp


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
