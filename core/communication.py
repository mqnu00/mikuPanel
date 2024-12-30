import asyncio
import multiprocessing
import uuid
from asyncio.queues import Queue
from multiprocessing import Manager
from multiprocessing.managers import SyncManager
from multiprocessing.pool import Pool

share = None
process_pool = None


class Message(object):

    def __init__(self,
                 uid: str):
        self.manager: SyncManager = Manager()
        self.uid = uid
        self.action_info = self.manager.dict()
        self.recv_queue = self.manager.Queue()
        self.send_queue = self.manager.Queue()


def pool_initializer():
    pass


def init_pool(num: int):
    global process_pool
    process_pool: Pool = multiprocessing.Pool(num, initializer=pool_initializer, initargs=())


def init_ipc():
    global share
    share = Message(str(uuid.uuid1()))
