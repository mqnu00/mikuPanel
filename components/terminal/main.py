import asyncio
from typing import Dict

from websockets.asyncio.server import ServerConnection

from components.base_component import BaseComponent
from components.terminal.terminal import Terminal
from core.component_init import Config
from utils.log_util import log
from core import communication
import uuid


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
        uid = str(uuid.uuid1())
        terminals['123'] = terminal
        return uid

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
        return False

    def handle(self):
        from components.terminal.terminal import SSHInfo, Terminal
        from tests import server_password
        self.create_terminal(SSHInfo(
            host=server_password.host,
            port=server_password.port,
            username=server_password.username,
            password=server_password.password
        ))

        def receive():

            while True:
                if not communication.share.recv_queue.empty():
                    msg = communication.share.recv_queue.get()
                    if not self.send('123', msg):
                        break
                if not self.check_terminal('123'):
                    break
            log.info("recv done")

        def send_to():
            gen = self.recv('123')
            while True:
                try:
                    communication.share.send_queue.put(next(gen))
                except StopIteration:
                    break
            communication.share.send_queue.put(None)
            log.info('send done')

        from concurrent.futures import ThreadPoolExecutor
        thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="terminal_")
        recv_future = thread_pool.submit(receive)
        send_future = thread_pool.submit(send_to)
        thread_pool.shutdown()
