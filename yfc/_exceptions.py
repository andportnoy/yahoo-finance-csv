class Yahoo404Error(Exception):
    def __init__(self, message):
        self.message = message


class BadTickersFormat(Exception):
    def __init__(self, message):
        self.message = message
