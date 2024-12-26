import asyncio
from typing import Dict

from websockets.asyncio.server import ServerConnection

from components.base_component import BaseComponent
from components.terminal.terminal import Terminal
from core.component_init import Config
from utils.log_util import log


class TerminalComponent(BaseComponent):

    def __init__(self):
        terminals: Dict[str, Terminal] = {}

        self.config = Config(
            instance={
                "terminals": terminals
            },
            is_async=False
        )

    def create_terminal(self, info, *args, **kwargs):
        terminal = Terminal(info)
        terminal.connect_to_terminal()

        terminals: Dict[str, Terminal] = self.config.instance.get('terminals')
        terminals['123'] = terminal

    def check_terminal(self, uid, *args, **kwargs) -> Terminal | bool:
        try:
            terminal: Terminal = self.config.instance.get('terminals').get(uid)
            return terminal
        except IndexError:
            return False
        except Exception:
            return False

    def get_terminal(self, uid, *args, **kwargs):
        return self.check_terminal(uid)

    def del_terminal(self, uid: str, *args, **kwargs):
        terminal: Terminal = self.config.instance.get('terminals')[uid]
        terminal.close()
        del self.config.instance.get('terminals')[uid]

    def send(self, uid: str, msg: str, *args, **kwargs):
        try:
            terminal: Terminal = self.config.instance.get('terminals')[uid]
        except Exception:
            return False
        if not terminal.send_to_terminal(msg):
            self.del_terminal(uid)
            return False
        return True

    def recv(self, uid: str, *args, **kwargs):
        while True:
            try:
                terminal: Terminal = self.config.instance.get('terminals')[uid]
                res = terminal.recv_from_terminal()
                if not res:
                    self.del_terminal(uid)
                    break
                yield res
            except Exception:
                log.exception("recv_error")
                continue
        yield False

    async def handle(self, websocket: ServerConnection):
        from components.terminal.terminal import SSHInfo, Terminal
        from tests import server_password
        self.create_terminal(SSHInfo(
            host=server_password.host,
            port=server_password.port,
            username=server_password.username,
            password=server_password.password
        ))

        async def receive():

            async for msg in websocket:
                if not self.send('123', msg):
                    break
            log.info("recv done")

        async def send_to():
            async def async_wrapper():
                gen = self.recv('123')
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
            log.info('send done')
            await websocket.close()

        await asyncio.gather(receive(), send_to())
