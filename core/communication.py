import importlib
import logging
import multiprocessing
from multiprocessing.pool import Pool
from utils.log_util import setup_logger
from sqlalchemy import create_engine, Engine, select, Executable, text, insert, Column, Integer, String, Row
from sqlalchemy.orm import Query, declarative_base, DeclarativeBase, sessionmaker
from multiprocessing.managers import SyncManager
import pymysql
# from core.sqlEngine import SqlEngine


class Message(object):

    def __init__(self):
        self.action_info = manager.dict()
        self.recv_queue = manager.Queue()
        self.send_queue = manager.Queue()


manager: SyncManager = None
share: dict[str, Message] | Message = {}
process_pool: Pool = None
SqlBase: DeclarativeBase = None
# sql_engine: SqlEngine = None


def pool_initializer():
    pass


def init_pool(num: int):
    global process_pool
    process_pool = multiprocessing.Pool(num, initializer=pool_initializer, initargs=())


def init_ipc(info: str = None):
    if info:
        global share
        share[info] = Message()
    else:
        # 保证 manager 只有一个
        global manager
        manager = multiprocessing.Manager()


# todo single_sql_process
def init_sql(num: int):
    global share


if __name__ == '__main__':
    from components.terminal.terminal import SSHInfo
    # init_ipc()
    # init_sql(4)
    #
    #
    # class Test(sql_engine.SqlBase):
    #     __tablename__ = 'test_2'
    #
    #     id = Column(Integer, primary_key=True, autoincrement=True)
    #     name = Column(String(100), nullable=False)
    #
    #
    # sql_engine.execute(insert(
    #     table=Test
    # ).values(name='Alice'))
    #
    # sql_engine.execute(text("insert into test_2 (name) values ('123');"))
