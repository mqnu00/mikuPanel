import asyncio
import json
import pprint
import threading
import traceback
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
        self.terminals: Dict[str, Terminal] = {}

    def create_terminal(self, info, *args, **kwargs):
        terminal = Terminal(info)
        terminal.connect_to_terminal()

        uid = str(uuid.uuid1())
        self.terminals[uid] = terminal
        return uid

    def check_terminal(self, uid, *args, **kwargs) -> Terminal | bool:
        try:
            return self.terminals.get(uid)
        except IndexError:
            log.info(f"no terminal index is {uid}")
            return False
        except Exception:
            log.exception("unknown exc")
            return False

    def get_terminal(self, uid, *args, **kwargs):
        return self.check_terminal(uid)

    def del_terminal(self, uid: str, *args, **kwargs):
        terminal: Terminal = self.get_terminal(uid)
        if terminal:
            log.info(traceback.format_stack())
            log.info(uid)
            terminal.close()
            try:
                del self.terminals[uid]
            except KeyError:
                log.info(f"{uid} already delete")
            return True
        else:
            log.info(f"terminal {uid} not exist")
            return False

    def send(self, uid: str, msg: str, *args, **kwargs):
        terminal: Terminal = self.get_terminal(uid)
        # None client 连接中断
        if not terminal:
            return False
        if not msg or not terminal.send_to_terminal(msg):
            self.del_terminal(uid)
            return False
        return True

    def recv(self, uid: str, *args, **kwargs):
        while True:
            try:
                terminal: Terminal = self.get_terminal(uid)
                res = terminal.recv_from_terminal()
                if not res:
                    break
                yield res
            except TimeoutError:
                log.info("recv timeout")
            except Exception:
                log.exception("recv_error")
                continue
        return False

    def handle(self):
        from components.terminal.terminal import SSHInfo, Terminal
        from tests import server_password

        def receive():

            while True:
                if not communication.share.recv_queue.empty():

                    msg = communication.share.recv_queue.get()
                    # websocket 连接关闭
                    if not msg:
                        uids = list(self.terminals.keys())
                        for uid in uids:
                            self.del_terminal(uid)
                        break
                    info: dict = json.loads(msg)
                    do_info = info.get('do')

                    if do_info == 'create':
                        # create terminal return uid
                        # msg = {
                        #     "do": "create",
                        #     "data": {
                        #         "host": "",
                        #         "port": 22,
                        #         "username": "",
                        #         "password": ""
                        #     }
                        # }

                        uid = self.create_terminal(SSHInfo(
                            host=server_password.host,
                            port=server_password.port,
                            username=server_password.username,
                            password=server_password.password
                        ))
                        communication.share.send_queue.put(json.dumps({
                            "do_return": "create",
                            "data": {
                                "uid": uid
                            }
                        }))

                        gen = self.recv(uid)
                        recv_thread = threading.Thread(target=send_to, args=(gen, uid))
                        recv_thread.start()

                    elif do_info == 'send':
                        # send msg return 成功 失败
                        # msg = {
                        #     "do": "send",
                        #     "data": {
                        #         "uid": "",
                        #         "msg": ""
                        #     }
                        # }

                        data: dict = info.get('data')
                        uid = data.get('uid')
                        msg = data.get('msg')
                        if not self.send(uid, msg):
                            break
                        if not self.check_terminal(uid):
                            break

                    elif do_info == 'delete':

                        data: dict = info.get('data')
                        uid = data.get('uid')
                        self.del_terminal(uid)

            log.info("recv done")

        def send_to(gen, uid):

            while True:
                try:
                    msg = next(gen)
                    # todo 无法处理不可序列化的二进制数据
                    communication.share.send_queue.put(json.dumps({
                        "do_return": "send",
                        "data": {
                            "uid": uid,
                            "msg": msg
                        }
                    }))
                except StopIteration:
                    break
            # chan close
            # communication.share.send_queue.put(None)
            # communication.share.recv_queue.put(None)
            self.del_terminal(uid)
            communication.share.send_queue.put(json.dumps({
                "do_return": "delete",
                "data": {
                    "uid": uid
                }
            }))
            log.info('send done')

        thread = threading.Thread(target=receive)
        thread.start()
        thread.join()
