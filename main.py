import asyncio
import json

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from utils.sysInfo import cpu, memory, network

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


