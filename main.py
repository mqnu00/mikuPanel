import asyncio
import json
import subprocess

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from utils.sysInfo import cpu, memory, network, disk

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.websocket("/sysInfo")
async def sys_info(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text('123')
    await websocket.close()

@app.websocket("/cpu")
async def cpu_info(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            await asyncio.sleep(1)
            await websocket.send_text(str(cpu.get_cpu_per()))
        except WebSocketDisconnect:
            break

@app.websocket("/memory")
async def memory_info(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            await asyncio.sleep(1)
            used, free, per = memory.get_memory_per()
            await websocket.send_text(json.dumps({
                "used": used,
                "free": free,
                "value": per
            }))
        except WebSocketDisconnect:
            break


@app.websocket("/network")
async def network_info(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            send, recv = await network.get_network_per()
            await websocket.send_text(json.dumps({
                "send": send,
                "recv": recv
            }))
        except WebSocketDisconnect:
            break


@app.websocket("/disk")
async def disk_info(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            read, write = await disk.get_disk_per()
            await websocket.send_text(json.dumps({
                "read": read,
                "write": write
            }))
        except WebSocketDisconnect:
            break



from fastapi import FastAPI, WebSocket
import subprocess
import base64
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    process = subprocess.Popen(
        ["cmd.exe"],  # 或 "powershell.exe"
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    # 确保在 websocket 连接断开时终止进程
    try:
        # 用于从进程读取输出
        async def read_from_process():
            while True:
                output = await asyncio.to_thread(process.stdout.readline)
                error = await asyncio.to_thread(process.stderr.readline)
                print(output)
                print(error)
                if output:
                    await websocket.send_text(output.encode('utf8'))
                else:
                    break

        # 用于将输入发送到进程
        async def write_to_process():
            while True:
                data = await websocket.receive_text()
                print(f"Received from frontend: {data}")
                data = json.loads(data)

                if data['type'] == 'terminal':
                    # 解码 base64 编码的命令并执行
                    command = base64.b64decode(data['data']['base64']).decode('utf-8')
                    command += '\n'
                    print(f"Executing command: {command}")

                    # 执行命令并获取输出
                    process.stdin.write(command)
                    process.stdin.flush()

                elif data['type'] == 'resize':
                    # 处理终端大小调整（如果有必要）
                    print(f"Received resize request: {data['data']}")

                # 将从客户端接收到的数据传递到 cmd 进程的输入
                if data.get('type') == 'input' and process.stdin:
                    process.stdin.write(data['data'])
                    process.stdin.flush()

        # 并行运行读写任务
        await asyncio.gather(read_from_process(), write_to_process())

    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    finally:
        # 确保终止进程
        process.terminate()
        print("Process terminated.")