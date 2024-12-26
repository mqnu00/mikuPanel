from websockets.asyncio.server import ServerConnection


class BaseComponent(object):

    def __init__(self):
        pass

    def handle(self, websocket: ServerConnection):
        pass
