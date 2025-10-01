class Duplicate(Exception):
    def __init__(self, msg:str):
        self.msg = msg

class Missing(Exception):
    def __init__(self, msg:str):
        self.msg = msg