import asyncio

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from utils.sysInfo import cpu

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.websocket("utils/sysInfo")
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

