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
            from components.terminal.main import create_terminal, del_terminal, send, recv, check_terminal
            from components.terminal.terminal import SSHInfo, Terminal
            from tests import server_password
            create_terminal(SSHInfo(
                host=server_password.host,
                port=server_password.port,
                username=server_password.username,
                password=server_password.password
            ))

            running = True

            async def receive():

                async for msg in websocket:
                    if not send('123', msg):
                        break
                print("recv done")

            async def send_to():
                async def async_wrapper():
                    gen = recv('123')
                    while True:
                        try:
                            # 这里使用 loop.run_in_executor 来运行同步代码
                            value = await asyncio.to_thread(next, gen)
                            yield value
                        except StopIteration as e:
                            # 处理返回值
                            res = e.value
                            break
                            pass
                    yield res

                async for res in async_wrapper():
                    if res:
                        await websocket.send(res)
                    else:
                        break
                print('send done')
                await websocket.close()

            await asyncio.gather(receive(), send_to())

        except websockets.exceptions.ConnectionClosed:
            log.info('server closed by client')
        except Exception:

            log.exception('wrong')


if __name__ == '__main__':
    # 启动主任务
    server = MikuServer(8000)
    server.start()
