import main
from utils import alert


class NotSupportedLanguageException(Exception):
    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        if self.error is None:
            return "language is not supported"
        return self.error


current_lang = main.language


class CouldNotSearchLanguageDataException(Exception):
    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        if self.error is None:
            return "Couldn't search language data"
        return self.error


def get_current_lang():
    return current_lang


def change_lang(langcode: str):
    global current_lang
    if langcode in get_support_lang():
        current_lang = langcode
    else:
        raise NotSupportedLanguageException(f"Not Supported language: {langcode}")


def get_text(langpath: str, fallback: str = None):
    if fallback is None:
        fallback = "ko"
    with open(f"././lang/{get_current_lang()}.lang", 'r', encoding="utf-8") as lang:
        for line in lang:
            if line.startswith(langpath):
                if line[line.index(":") + 2:].replace("<br>", "\n") == "" or None:
                    with open(f"././lang/{fallback}.lang", 'r', encoding='utf-8') as fi:
                        for line2 in fi:
                            if line2.startswith(langpath):
                                return line2[line2.index(":") + 2:].replace("<br>", "\n")
                else:
                    return line[line.index(":") + 2:].replace("<br>", "\n")


def get_support_lang():
    return ['ko', 'en', 'jp']
