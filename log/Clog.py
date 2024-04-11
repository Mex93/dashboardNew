class Clog:
    __log_enable = True

    def __init__(self):
        pass

    @staticmethod
    def lprint(text: str):
        if Clog.__log_enable:
            print(text)
