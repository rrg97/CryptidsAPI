class MissingException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

class DuplicateException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg