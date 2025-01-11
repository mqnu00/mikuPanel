from typing import List


class Config(object):

    def __init__(self,
                 sql_tabel: List[object],
                 is_need_sql: bool = False,
                 is_async: bool = False):
        # self.instance = instance
        self.is_async = is_async
