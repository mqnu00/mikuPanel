import asyncio
import multiprocessing

from sqlalchemy import Column, Integer, String, insert

from core import communication

from ws.server import MikuServer
from core.LoopManager import loop_manager

if __name__ == '__main__':
    multiprocessing.freeze_support()
    # multiprocessing.set_start_method()
    communication.init_ipc()
    communication.init_pool(4)
    communication.init_sql()

    # from core.sqlEngine import sql_service
    # sql_service.start()
    server = MikuServer(8000)
    server.start()
