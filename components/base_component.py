from websockets.asyncio.server import ServerConnection

from core import communication
from core.communication import Message


class BaseComponent():

    def __init__(self, uid):
        self.uid = uid
        self.role = 1
        self.msg: Message = communication.share.get(uid)

    def handle(self, uid):
        pass

    def read(self, is_sync=True):
        return self.msg.read(role=self.role, is_sync=is_sync)

    def write(self, content, is_sync=True):
        return self.msg.write(content, role=self.role, is_sync=is_sync)