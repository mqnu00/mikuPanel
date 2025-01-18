from typing import List


class Config(object):

    def __init__(self,
                 sql_table: List[str] = None,
                 is_need_sql: bool = False,
                 is_async: bool = False):
        # self.instance = instance
        self.is_need_sql = is_need_sql
        self.sql_table = sql_table
        self.is_async = is_async
