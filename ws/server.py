import asyncio
import json
import os
import pprint
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import List, Coroutine, Any

import aiohttp_cors
from aiohttp import web
from aiohttp.web_ws import WebSocketResponse, WSMsgType

from mission import mission
from utils.log_util import log

# 假设 core 和其他模块已经适配为兼容 aiohttp
from core.communication import share
from core import communication
from core.message.action.dispatch import action_dispatch
from aiohttp_cors import setup as setup_cors

class MikuServer(object):
    def __init__(self, port):

        self.port = port
        self.app = web.Application()
        self.cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })


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
                        await communication.share[uid].write(msg.data, 1, is_sync=False)
                        # await asyncio.to_thread(communication.share[uid].recv_queue.put, msg.data)
                    elif msg.type == WSMsgType.CLOSED:

                        await asyncio.to_thread(communication.share[uid].recv_queue.put, None)

                        break
                log.info(f'{uid} recv closed')
                await asyncio.to_thread(communication.share[uid].recv_queue.put, json.dumps({
                    "do": "close"
                }))
                log.info(uid.split('-')[0])
                if uid.split('-')[0] == "menu":
                    log.info("menu")
                    await asyncio.to_thread(communication.share["menu-component"].send_queue.put, {
                        "do": "close"
                    })
                return 'recv_done'

            async def send_msg():
                nonlocal check_status
                while not check_status:
                    await asyncio.sleep(0)
                while True:
                    msg = await communication.share[uid].read(1, is_sync=False)
                    # msg = await asyncio.to_thread(communication.share[uid].send_queue.get)
                    if not msg:
                        break
                    await ws.send_str(msg)
                log.info(f'{uid} send closed')

            async def check_end():
                log.info('server.handle')
                msg = await ws.receive_str()
                log.info(msg)
                nonlocal uid
                # 创建一个自定义的线程池
                executor = ThreadPoolExecutor(max_workers=1)
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(executor, action_dispatch, msg)
                component_name = None
                if len(result) == 2:
                    uid, future = result
                else:
                    uid, component_name, future = result
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
                if component_name:
                    try:
                        modules_to_delete = [name for name in sys.modules if name.startswith(component_name)]

                        for module_name in modules_to_delete:
                            if module_name in sys.modules:
                                del sys.modules[module_name]
                                log.info(f"已删除模块: {module_name}")
                    except Exception as e:
                        log.exception(e)

            start_component_task = asyncio.create_task(check_end())
            tasks: List[asyncio.Task] = [asyncio.create_task(recv_msg()), asyncio.create_task(send_msg())]
            done, pending = await asyncio.wait([start_component_task, *tasks], return_when=asyncio.FIRST_COMPLETED)
            # 检查哪个任务完成了
            # for task in done:
            #     result = task.result()
            #     if result == "recv_done":
            #         log.info("recv_msg completed, cancelling other tasks")
            #         for pending_task in pending:
            #             pending_task.cancel()
            #             try:
            #                 await pending_task
            #             except asyncio.CancelledError:
            #                 log.info(f"Task {pending_task} was cancelled")
            return ws

            # HTTP 路由
        async def handle_http(request: web.Request):

            if request.path == '/install_component':
                # 处理文件上传
                from core.message.action import component_config
                return await component_config.save_plugin(request)
            else:
                return web.Response(text="Hello, this is the HTTP server!", content_type="text/plain")

        self.app.router.add_get('/', handle_ws)
        # self.app.router.add_get('/{tail:.*}', handle_http)
        # 配置 CORS 允许所有来源
        self.app.router.add_get('/{tail:.*}', handle_http)
        self.cors.add(self.app.router.add_post('/{tail:.*}', handle_http))

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