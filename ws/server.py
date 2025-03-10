# 启动 WebSocket 服务器
import asyncio
import json
import multiprocessing
import pprint
import uuid
from asyncio import Task
from concurrent.futures import Future
from multiprocessing.pool import ApplyResult
from typing import Callable, Awaitable, List, Coroutine, Any

import websockets
from websockets import Headers
from websockets.asyncio.connection import Connection
from websockets.asyncio.server import ServerConnection, Server
from websockets.http11 import Request, Response, SERVER

from mission import mission
from utils.log_util import log


class MikuServer(object):

    def __init__(self, port):
        self.port = port
        self.server: Server = None

    def start(self):
        multiprocessing.current_process().name = 'Server'
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._prepare_server())
        loop.run_until_complete(task)

    async def _prepare_server(self):
        async def start_server():
            # 在这里直接传递处理函数，它会自动提供 websocket 和 path 参数
            server = await websockets.serve(self.handle,
                                            "0.0.0.0", self.port,
                                            max_size=50 * 1024 * 1024,
                                            process_request=self._process_requests,
                                            logger=log)
            await server.start_serving()
            log.info(f"WebSocket 服务器已启动，监听 ws://localhost:{self.port} 🎉")
            self.server = server
            await server.wait_closed()

        return await start_server()

    async def _process_requests(self, websocket: ServerConnection, request: Request):
        if request.path != '/':
            return Response(status_code=404, reason_phrase='Not Found', headers=Headers({}))

    async def handle(self, websocket: ServerConnection):
        try:

            uid: str
            check_status = False


            from core.communication import share
            from core import communication

            async def recv_msg():
                while not check_status:
                    await asyncio.sleep(0)
                async for msg in websocket:
                    await asyncio.to_thread(communication.share[uid].recv_queue.put, msg)
                # client 断开连接
                await asyncio.to_thread(communication.share[uid].recv_queue.put, None)
                log.info('websocket recv close')

            async def send_msg():
                while not check_status:
                    await asyncio.sleep(0)
                while True:
                    msg = await asyncio.to_thread(communication.share[uid].send_queue.get)
                    # None 没有消息
                    if not msg:
                        break
                    await websocket.send(msg)
                # 服务端停止发送
                log.info('websocket send close')

            async def check_end():
                log.info('server.handle')

                msg: str = await websocket.recv()
                from core.message.action.dispatch import action_dispatch
                future: Future
                log.info('dispatch')
                nonlocal uid
                uid, future = await asyncio.to_thread(action_dispatch, msg)
                log.info("测试dispatch输出")
                log.info(uid)
                log.info(future)
                nonlocal check_status
                check_status = True
                res = await asyncio.to_thread(future.result)
                log.info(f'进程运行完毕：{res}')
                if res:
                    await websocket.close()

                del communication.share[uid]
            start_component_task = asyncio.create_task(check_end())
            tasks: List[Task] = [asyncio.create_task(recv_msg()), asyncio.create_task(send_msg())]
            await asyncio.gather(start_component_task, *tasks)


        except websockets.exceptions.ConnectionClosed:
            log.info('server closed by client')
        except Exception:

            log.exception('wrong')


if __name__ == '__main__':
    # 启动主任务
    server = MikuServer(8000)
    server.start()
