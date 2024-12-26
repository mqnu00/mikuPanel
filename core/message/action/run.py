import asyncio
import importlib

from websockets.server import ServerConnection


async def execute(websocket: ServerConnection, action_info: dict):
    component_name = action_info.get('componentName')
    if component_name == 'terminal':
        module = importlib.import_module(f'components.terminal.main')
        component_class = getattr(module, 'TerminalComponent')
        component_instance = component_class()
        await component_instance.handle(websocket)
