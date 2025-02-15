from __future__ import annotations
import multiprocessing
from multiprocessing.pool import Pool
from multiprocessing.managers import SyncManager
from multiprocessing import Queue
from core.sqlEngine import SqlEngine
import asyncio


class Message(object):

    def __init__(self):
        self.action_info = manager.dict()
        self.recv_queue = manager.Queue()
        self.send_queue = manager.Queue()

    # todo ipc format read write

    @staticmethod
    def read(q: Queue, is_async=True):
        if is_async:
            loop = asyncio.get_event_loop()
            msg = loop.run_until_complete(asyncio.to_thread(q.get()))
        else:
            try:
                msg = q.get_nowait()
            except Exception:
                return False
        return msg

    @staticmethod
    def write():
        pass


manager: SyncManager = None
share: dict[str, Message] | Message = {}
process_pool: Pool = None
sql_engine: SqlEngine = None


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


# todo single_sql_process_communication
def init_sql():
    global sql_engine
    global share
    from core import sqlEngine
    sql_engine = sqlEngine.sql_engine
    share['sql'] = Message()


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
