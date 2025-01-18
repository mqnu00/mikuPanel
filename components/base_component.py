from websockets.asyncio.server import ServerConnection

from core.component_init import Config


class BaseComponent(object):

    def __init__(self):
        self.config = Config()
        pass

    def handle(self):
        pass
