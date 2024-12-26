class Config(object):

    def __init__(self, instance: dict, is_async: bool = False):
        self.instance = instance
        self.is_async = is_async
