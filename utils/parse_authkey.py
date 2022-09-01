"""
    #제작: @17th
    #최종 수정일: 2022년 08월 27일
"""


class CouldNotSearchAuthKeyException(Exception):
    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        if self.error is None:
            return "Couldn't search auth key"
        return self.error


def get_auth_key(key: str):
    with open(f"././.auth", 'r', encoding="utf-8") as auth:
        for line in auth:
            if line.startswith(key):
                if line[line.index(":") + 2:].replace("<br>", "\n") == "" or None:
                    raise CouldNotSearchAuthKeyException()
                else:
                    return line[line.index(":") + 2:].strip()
