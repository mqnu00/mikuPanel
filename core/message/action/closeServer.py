from ws.server import MikuServer


async def execute(server: MikuServer):
    server.server.close()
    await server.server.wait_closed()
