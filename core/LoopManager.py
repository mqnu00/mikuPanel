import asyncio
import sys
from asyncio import AbstractEventLoop, Future
from threading import Thread
from utils.log_util import log
from typing import Optional, Callable


def new_event_loop():
    if sys.platform == 'win32':
        return asyncio.ProactorEventLoop()
    else:
        return asyncio.new_event_loop()


class Loop(object):

    def __init__(self,
                 loop: AbstractEventLoop,
                 name: str,
                 thread: Thread
                 ):

        self.loop = loop
        self.name = name,
        self.thread = thread

    @classmethod
    def _set_loop(cls, loop: AbstractEventLoop):

        asyncio.set_event_loop(loop)

        try:
            loop.run_forever()
        finally:
            log.info(asyncio.Task.all_tasks(loop))
            loop.shutdown_asyncgens()
            loop.close()

    @classmethod
    def create(cls,
               thread_name: str):

        loop = new_event_loop()
        thread = Thread(
            name=thread_name,
            target=cls._set_loop,
            args=(loop,),
            daemon=True
        )
        thread.start()

        return cls(
            loop,
            thread_name,
            thread
        )

    def create_future(self):
        return self.loop.create_future()

    def ensure_future(self, coro):
        return asyncio.ensure_future(coro, loop=self.loop)
