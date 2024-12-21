import asyncio
import base64
import json
import pprint
import subprocess

import uvicorn

import sshInfo

import paramiko
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


@app.websocket("/terminals/")
async def terminals(websocket: WebSocket):
    await websocket.accept()
    client = paramiko.SSHClient()
    # 自动添加策略，保存服务器的主机名和密钥信息
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接SSH服务端，以用户名和密码进行认证
    client.connect(hostname=sshInfo.host, port=sshInfo.port, username=sshInfo.username, password=sshInfo.pwd)
    chan = client.invoke_shell('xterm')
    chan.settimeout(0)

    async def recv_msg():
        while True:
            msg = await websocket.receive_text()
            # chan.send(msg.encode('utf8'))
            print("???"+msg)
            recv_info: dict = json.loads(msg)
            pprint.pprint(recv_info)
            recv_type = recv_info.get('type')
            if recv_type == 'resize':
                chan.resize_pty(width=recv_info.get("cols"), height=recv_info.get("rows"))
            elif recv_type == 'cmd':
                print(recv_info.get('msg').encode('utf8'))
                chan.send(recv_info.get('msg').encode('utf8'))


    async def send_msg():
        while True:
            try:
                rec = chan.recv(1024)
                # print(rec.decode('utf8'), end='')
                await websocket.send_text(rec.decode('utf8'))
            except Exception:
                await asyncio.sleep(0.1)
                pass

    await asyncio.gather(recv_msg(), send_msg())


if __name__ == '__main__':
    # 运行fastapi程序
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
