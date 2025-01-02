import asyncio
import multiprocessing
from core import communication

from ws.server import MikuServer

if __name__ == '__main__':
    multiprocessing.freeze_support()
    communication.init_ipc()
    communication.init_pool(4)
    server = MikuServer(8000)
    server.start()
