class Clog:
    __log_enable = False

    def __init__(self):
        pass

    @classmethod
    def lprint(cls, text: str):
        if cls.__log_enable:
            print(text)
