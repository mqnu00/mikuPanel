# 启动 WebSocket 服务器
import asyncio
import pprint

import websockets
from websockets.asyncio.server import ServerConnection


async def handle(websocket: ServerConnection):
    try:
        pass
    except websockets.ConnectionClosed:
        pass


async def main():
    # 在这里直接传递处理函数，它会自动提供 websocket 和 path 参数
    server = await websockets.serve(handle, "localhost", 8000)
    print("WebSocket 服务器已启动，监听 ws://localhost:8000 🎉")
    await server.wait_closed()


# 启动主任务
asyncio.run(main())