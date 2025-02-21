from __future__ import annotations
import multiprocessing
from multiprocessing.pool import Pool
from multiprocessing.managers import SyncManager
from multiprocessing import Queue
import asyncio


class Message(object):

    def __init__(self, role: str = None):
        self.role = role
        self.action_info = manager.dict()
        self.recv_queue = manager.Queue()
        self.send_queue = manager.Queue()

    # todo ipc format read write

    @staticmethod
    async def read_queue_async(q: Queue):
        while True:
            if q.not_empty:
                try:
                    return q.get_nowait()
                except Exception:
                    await asyncio.sleep(0)
            else:
                await asyncio.sleep(0)

    @staticmethod
    def read_queue_sync(q: Queue):
        return q.get()

    @staticmethod
    async def send_queue_async(q: Queue, msg):
        while True:
            if q.not_full:
                try:
                    q.put_nowait(msg)
                    return True
                except Exception:
                    await asyncio.sleep(0)
            else:
                await asyncio.sleep(0)

    @staticmethod
    def send_queue_sync(q: Queue, msg):
        q.put(msg)
        return True

    def set_role(self, role: int):
        if role == 0:
            self.role = 'sender'
        else:
            self.role = 'recipient'

    def is_ready(self, check: str):
        if self.role == 'recipient':
            if check == 'recv':
                return self.recv_queue.not_empty
            else:
                return self.send_queue.not_full

        else:
            if check == 'recv':
                return self.send_queue.not_empty
            else:
                return self.recv_queue.not_full

    def read(self, is_sync: bool = True):
        if self.role == 'recipient':
            if is_sync:
                return self.read_queue_sync(self.recv_queue)
            else:
                return self.read_queue_async(self.recv_queue)
        else:
            if is_sync:
                return self.read_queue_sync(self.send_queue)
            else:
                return self.read_queue_async(self.send_queue)

    def write(self, is_sync: bool = True):
        if self.role == 'recipient':
            if is_sync:
                return self.read_queue_sync(self.send_queue)
            else:
                return self.read_queue_async(self.send_queue)
        else:
            if is_sync:
                return self.read_queue_sync(self.recv_queue)
            else:
                return self.read_queue_async(self.recv_queue)


manager: SyncManager = None
share: dict = {}
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


# share.sql.uid from users
def init_sql():
    global share
    share['sql'] = Message()


if __name__ == '__main__':
    from components.terminal.terminal import SSHInfo

    init_ipc()
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
