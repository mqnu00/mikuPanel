import asyncio
from asyncio.queues import Queue


class MessageQueue(object):

    def __init__(self,
                 uid: str,
                 component_type: str,
                 tran: Queue):
        self.uid = uid
        self.component_type = component_type
        self.chan = tran


queues = MessageQueue('1', 'terminal', Queue())
queuer = MessageQueue('2', 'terminal', Queue())
