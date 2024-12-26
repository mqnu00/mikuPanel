# 启动 WebSocket 服务器
import asyncio
import pprint
from typing import Callable, Awaitable

import websockets
from websockets import Headers
from websockets.asyncio.connection import Connection
from websockets.asyncio.server import ServerConnection
from websockets.http11 import Request, Response, SERVER

from mission import mission
from utils.log_util import log


class MikuServer(object):

    def __init__(self, port):
        self.port = port
        pass

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._prepare_server(self))
        loop.run_forever()
        pass

    @staticmethod
    async def _prepare_server(self):
        async def start_server():
            # 在这里直接传递处理函数，它会自动提供 websocket 和 path 参数
            server = await websockets.serve(self.handle,
                                            "localhost", self.port,
                                            max_size=50 * 1024 * 1024,
                                            process_request=self._process_requests,
                                            logger=log)
            await server.start_serving()
            log.info(f"WebSocket 服务器已启动，监听 ws://localhost:{self.port} 🎉")
            await server.wait_closed()

        return await start_server()

    async def _process_requests(self, websocket: ServerConnection, request: Request):
        if request.path != '/':
            return Response(status_code=404, reason_phrase='Not Found', headers=Headers({}))

    async def handle(self, websocket: ServerConnection):
        try:
            from components.terminal.main import test
            await test(websocket)
        except websockets.exceptions.ConnectionClosed:
            log.info('server closed by client')
        except Exception:

            log.exception('wrong')


if __name__ == '__main__':
    # 启动主任务
    server = MikuServer(8000)
    server.start()
