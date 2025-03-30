from __future__ import annotations
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import Pool
from multiprocessing.managers import SyncManager
from multiprocessing import Queue
import asyncio
import queue


class Message(object):

    def __init__(self):
        self.action_info = manager.dict()
        self.recv_queue = manager.Queue()
        self.send_queue = manager.Queue()

    # todo ipc format read write

    @staticmethod
    async def read_queue_async(q: Queue):
        while True:
            if not q.empty():
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
            if not q.full():
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

    def is_ready(self, check: str, role):
        if role == 0:
            if check == 'recv':
                return not self.recv_queue.empty()
            else:
                return not self.send_queue.full()

        else:
            if check == 'recv':
                return not self.send_queue.empty()
            else:
                return not self.recv_queue.full()

    def read(self, role, uid: str = None, is_sync: bool = True):
        if uid:
            if uid not in self.action_info:
                raise Exception(f"wrong uid {uid}")
            msg_queue: manager.Queue = self.action_info[uid]
            if is_sync:
                return self.read_queue_sync(msg_queue)
            else:
                return self.read_queue_async(msg_queue)
        if role == 0:
            if is_sync:
                return self.read_queue_sync(self.recv_queue)
            else:
                return self.read_queue_async(self.recv_queue)
        else:
            if is_sync:
                return self.read_queue_sync(self.send_queue)
            else:
                return self.read_queue_async(self.send_queue)

    def write(self, content, role, uid: str = None, is_sync: bool = True):
        if uid:
            if uid not in self.action_info:
                self.action_info[uid] = manager.Queue()
            msg_queue: manager.Queue = self.action_info[uid]
            if not is_sync:
                self.send_queue_async(msg_queue, content)
            else:
                self.send_queue_sync(msg_queue, content)
        if role == 0:
            if is_sync:
                return self.send_queue_sync(self.send_queue, content)
            else:
                return self.send_queue_async(self.send_queue, content)
        else:
            if is_sync:
                return self.send_queue_sync(self.recv_queue, content)
            else:
                return self.send_queue_async(self.recv_queue, content)


manager: SyncManager = None
share: dict = {}
ctx: dict = {}
process_pool: Pool = None
thread_pool: ThreadPoolExecutor = None
allow_router: bool = True


def pool_initializer():
    pass


def init_pool(num: int):
    global process_pool
    process_pool = multiprocessing.Pool(num, initializer=pool_initializer, initargs=())


def init_thread_pool(num: int = 10):
    """
    协程提交阻塞任务使用的线程池
    :param num:
    :return:
    """
    global thread_pool
    thread_pool = ThreadPoolExecutor(max_workers=num)


def init_ipc(info: str = None):
    if info:
        global share
        if not share.get(info, None):
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
    init_ipc('test')
    msg: Message = share.get('test')
    msg.write(content=123, role=1, uid='1122')
    print(msg.read(role=0, uid='1122'))
    print(msg.read(role=0, uid='1122'))
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
