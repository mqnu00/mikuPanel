import asyncio
import multiprocessing

from sqlalchemy import Column, Integer, String, insert

from core import communication

from ws.server import MikuServer

if __name__ == '__main__':
    multiprocessing.freeze_support()
    communication.init_ipc()
    communication.init_pool(4)
    # communication.init_sql(4)
    server = MikuServer(8000)
    server.start()
