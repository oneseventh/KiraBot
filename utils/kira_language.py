class NotSupportedLanguageException(Exception):
    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        if self.error is None:
            return "Language is not supported"
        return self.error


class CouldNotSearchLanguageDataException(Exception):
    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        if self.error is None:
            return "Couldn't search language data"
        return self.error


def get_text(langcode: str = None, langpath: str = None, fallback: str = None):
    if langcode is not ('ko' or 'en'):
        raise NotSupportedLanguageException(f"Not Supported language: {langcode}")
    if langpath is None:
        raise CouldNotSearchLanguageDataException()
    if fallback is None:
        fallback = "ko"
    with open(f"././lang/{langcode}.lang", 'r', encoding="utf-8") as lang:
        for line in lang:
            if line.startswith(langpath):
                if line[line.index(":") + 2:].replace("<br>", "\n") == "" or None:
                    with open(f"./lang/{fallback}.lang", 'r', encoding='utf-8') as fi:
                        for line2 in fi:
                            if line2.startswith(langpath):
                                return line2[line2.index(":") + 2:].replace("<br>", "\n")
                else:
                    return line[line.index(":") + 2:].replace("<br>", "\n")