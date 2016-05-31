class Yahoo404Error(Exception):
    def __init__(self, message):
        self.message = message


class BadTickersFormatError(Exception):
    def __init__(self, message):
        self.message = message
