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
    print("Guild ID: {0}".format(gid))
    for cid in channel_id:
        if cid == "{0}:{1}".format(str(gid), cid[cid.index(":") + 1:]):
            return int(cid[cid.index(":") + 1:])
    return None


def is_guild_registered(gid: int):
    for cid in channel_id:
        if cid.startswith(str(gid)):
            return True
    return False


# def set_log_channel(gid: int, cid: int):
#     """
#     로그 채널을 설정합니다.
#     :param gid: 바꿀 길드 ID
#     :param cid: 대상의 채널 ID (int)
#     """
#     if get_current_log_channel_id(gid) is None:
#         channel_id.append("{0}:{1}".format(gid, cid))
#         with open("./setting.txt", 'w') as setting_file:
#             setting_file.write("{0}:{1}".format(gid, cid))
#     else:
#         channel_id.remove("{0}:{1}".format(gid, get_current_log_channel_id(gid)))
#         channel_id.append("{0}:{1}".format(gid, cid))
#         with open("./settings.txt", 'r') as setting_read:
#             with open("./setting.txt", 'w') as setting_file:
#                 for setting in setting_read:
#                     if setting == "{0}:{1}".format(gid, get_current_log_channel_id(gid)):

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
