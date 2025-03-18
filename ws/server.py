import asyncio
import json
import uuid
from typing import List, Coroutine, Any
from aiohttp import web
from aiohttp.web_ws import WebSocketResponse, WSMsgType

from mission import mission
from utils.log_util import log

# 假设 core 和其他模块已经适配为兼容 aiohttp
from core.communication import share
from core import communication
from core.message.action.dispatch import action_dispatch


class MikuServer(object):
    def __init__(self, port):
        self.port = port
        self.app = web.Application()
        self.runner = None

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._prepare_server())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.stop())
        finally:
            loop.close()

    async def _prepare_server(self):
        async def handle_ws(request: web.Request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            uid: str = None
            check_status = False

            async def recv_msg():
                nonlocal check_status
                while not check_status:
                    await asyncio.sleep(0)
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        await asyncio.to_thread(communication.share[uid].recv_queue.put, msg.data)
                    elif msg.type == WSMsgType.CLOSED:
                        await asyncio.to_thread(communication.share[uid].recv_queue.put, None)
                        break
                log.info('websocket recv close')

            async def send_msg():
                nonlocal check_status
                while not check_status:
                    await asyncio.sleep(0)
                while True:
                    msg = await asyncio.to_thread(communication.share[uid].send_queue.get)
                    if not msg:
                        break
                    await ws.send_str(msg)
                log.info('websocket send close')

            async def check_end():
                log.info('server.handle')
                msg = await ws.receive_str()
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
                    await ws.close()
                del communication.share[uid]

            start_component_task = asyncio.create_task(check_end())
            tasks: List[asyncio.Task] = [asyncio.create_task(recv_msg()), asyncio.create_task(send_msg())]
            await asyncio.gather(start_component_task, *tasks)

            return ws

            # HTTP 路由
        async def handle_http(request: web.Request):
            return web.Response(text="Hello, this is the HTTP server!", content_type="text/plain")

        async def router_config(request: web.Request):
            log.info('路由设置')
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            # 模拟路由配置数据
            routes = [
                {"path": "/about", "name": "About", "component": "/src/plugins/1AboutView.vue"},
            ]

            # 将路由配置数据发送到前端
            await ws.send_json({"type": "routes", "routes": routes})

            await ws.close()

            return ws

        self.app.router.add_get('/', handle_ws)
        self.app.router.add_get('/RouterConfig', router_config)
        self.app.router.add_get('/http/{tail:.*}', handle_http)

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()
        log.info(f"WebSocket 服务器已启动，监听 ws://localhost:{self.port} 🎉")
        self.runner = runner

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            log.info("WebSocket 服务器已关闭")


if __name__ == '__main__':
    server = MikuServer(8000)
    server.start()