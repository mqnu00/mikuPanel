import asyncio
import multiprocessing
import uuid
from asyncio.queues import Queue
from multiprocessing import Manager
from multiprocessing.managers import SyncManager
from multiprocessing.pool import Pool


class Message(object):

    def __init__(self):
        self.action_info = manager.dict()
        self.recv_queue = manager.Queue()
        self.send_queue = manager.Queue()


manager: SyncManager = None
share: dict[str, Message] | Message = {}
process_pool: Pool = None


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


def init_sql():
    from sqlalchemy import create_engine
    from utils.log_util import setup_logger

    sql_log = setup_logger(
        name='sqlalchemy.engine',
        log_dir=rf'D:\program\python\code\mikuPanelGrpc\logs\test123'
    )
    sql_engine = create_engine("mysql+pymysql://root:123456@localhost/mikuserver?charset=utf8", pool_size=4)
    with sql_engine.connect() as conn:
        result = conn.execute("SELECT * FROM test_2")
        for row in result:
            print(row)
    # sql_engine.logger = sql_log


if __name__ == '__main__':
    init_sql()
