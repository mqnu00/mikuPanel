import asyncio
import logging
from typing import List, Dict

from components.terminal.terminal import Terminal, SSHInfo
from core.component_init import Config
from utils.log_util import log
from websockets.asyncio.server import ServerConnection
import uuid
from websockets.asyncio.server import ServerConnection

config: Config


def init():
    global config
    terminals: Dict[str, Terminal] = {}

    config = Config(
        instance={
            "terminals": terminals
        },
        is_async=False
    )

    return config


def create_terminal(info, *args, **kwargs):
    terminal = Terminal(info)
    terminal.connect_to_terminal()

    terminals: Dict[str, Terminal] = config.instance.get('terminals')
    terminals['123'] = terminal


def check_terminal(uid, *args, **kwargs) -> Terminal | bool:
    try:
        terminal: Terminal = config.instance.get('terminals').get(uid)
        return terminal
    except IndexError:
        return False
    except Exception:
        return False


def get_terminal(uid, *args, **kwargs):
    return check_terminal(uid)


def del_terminal(uid: str, *args, **kwargs):
    terminal: Terminal = config.instance.get('terminals')[uid]
    terminal.close()
    del config.instance.get('terminals')[uid]


def send(uid: str, msg: str, *args, **kwargs):
    try:
        terminal: Terminal = config.instance.get('terminals')[uid]
    except Exception:
        return False
    if not terminal.send_to_terminal(msg):
        del_terminal(uid)
        return False
    return True


def recv(uid: str, *args, **kwargs):
    while True:
        try:
            terminal: Terminal = config.instance.get('terminals')[uid]
            res = terminal.recv_from_terminal()
            if not res:
                del_terminal(uid)
                break
            yield res
        except Exception:
            log.exception("recv_error")
            continue
    yield False


init()


async def test(websocket: ServerConnection):
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


if __name__ == '__main__':
    init()
    from tests import server_password

    create_terminal(SSHInfo(
        host=server_password.host,
        port=server_password.port,
        username=server_password.username,
        password=server_password.password
    ))
