import asyncio
import sys
import threading
from asyncio import AbstractEventLoop, Future
from threading import Thread

from core import communication
from utils.log_util import log
from typing import Optional, Callable, Dict, Coroutine

MAIN_THREAD_NAME = 'MainThread'


def new_event_loop():
    if sys.platform == 'win32':
        return asyncio.ProactorEventLoop()
    else:
        return asyncio.new_event_loop()


class Loop(object):
    """
    将事件循环和线程绑定
    """

    def __init__(self,
                 loop: AbstractEventLoop,
                 name: str,
                 thread: Thread,
                 end_fut: Optional[Future]
                 ):

        self.loop = loop
        self.name = name,
        self.thread = thread
        self.end = end_fut

    @classmethod
    def _set_loop(cls, loop: AbstractEventLoop, end_callback: Callable[[], None]):

        asyncio.set_event_loop(loop)

        try:
            loop.run_forever()
        finally:
            log.info(asyncio.Task.all_tasks(loop))
            loop.shutdown_asyncgens()
            loop.close()
            end_callback()

    @classmethod
    def create(cls,
               thread_name: str,
               end_callback: Callable[[], None],
               end_fut: Future):

        loop = new_event_loop()
        thread = Thread(
            name=thread_name,
            target=cls._set_loop,
            args=(loop, end_callback),
            daemon=True
        )
        thread.start()

        return cls(
            loop,
            thread_name,
            thread,
            end_fut
        )

    @property
    def call_on_this(self):
        return asyncio.get_event_loop() is self.loop

    @property
    def call_on_thread(self):
        return threading.current_thread() is self.thread

    def run(self, coro: Coroutine | Future) -> Future:
        """
        封送异步对象至目标事件循环运行, 等待结果返回.
        """
        loop = self.loop
        current_loop = asyncio.get_event_loop()

        if current_loop is loop:
            return loop.create_task(coro)
        else:
            # 当前事件循环等待目标事件循环结果
            # 发送方法使用非threadsafe版本可能锁死线程
            return asyncio.wrap_future(
                asyncio.run_coroutine_threadsafe(coro, loop),
                loop=current_loop)

    def call_soon_threadsafe(self, func: Callable, *args):
        return self.loop.call_soon_threadsafe(func, *args)

    def call_coro_threadsafe(self, coro: Coroutine):
        """
        提交协程到运行中的事件循环
        :param coro:
        :return:
        """
        return self.loop.create_task(coro)

    def create_future(self):
        return self.loop.create_future()

    def ensure_future(self, coro):
        return asyncio.ensure_future(coro, loop=self.loop)

    def to_thread(self, func: Callable, *args):
        """
        提交阻塞任务
        :param func:
        :param args:
        :return:
        """
        future = self.loop.run_in_executor(func=func, executor=communication.thread_pool,*args)
        return future


class LoopManager(object):
    """
    分配事件循环
    """
    _lock = threading.Lock
    loops: Dict[str, Loop] = dict()

    def __init__(self):
        assert threading.current_thread().name is MAIN_THREAD_NAME
        loop = new_event_loop()
        self.loops[MAIN_THREAD_NAME] = Loop(
            loop=loop,
            name=MAIN_THREAD_NAME,
            thread=threading.current_thread(),
            end_fut=None
        )

        self._lock = threading.Lock()

    @property
    def main_loop(self):
        return self.loops[MAIN_THREAD_NAME]

    @property
    def main_raw_loop(self):
        return self.loops[MAIN_THREAD_NAME].loop

    def get_loop(self, key: str) -> Loop:
        return self.loops[key]

    def _get_or_add_loop_(self, key: str) -> Loop:
        if key not in self.loops:
            end_fut = self.main_raw_loop.create_future()

            def callback():
                log.info(f'线程[{key}]已关闭')
                self.main_loop.call_soon_threadsafe(
                    end_fut.set_result,
                    True)

            self.loops[key] = Loop.create(
                thread_name=key,
                end_callback=callback,
                end_fut=end_fut
            )
        return self.loops[key]

    def get_or_add_loop_threadsafe(self, key: str) -> Loop:
        if key not in self.loops:
            with self._lock:
                return self._get_or_add_loop_(key)
        return self.loops[key]


loop_manager = LoopManager()


if __name__ == '__main__':
    pass