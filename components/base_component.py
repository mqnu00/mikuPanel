import json

from core import communication
from core.communication import Message


class BaseComponent():

    def __init__(self, uid):
        self.uid = uid
        self.role = 0
        self.msg: Message = communication.share.get(uid)

    def handle(self, uid):
        pass

    def read(self, is_sync=True, **kwargs):
        return self.msg.read(role=self.role, is_sync=is_sync, **kwargs)

    def write(self, content, is_sync=True, **kwargs):
        return self.msg.write(content, role=self.role, is_sync=is_sync, **kwargs)
