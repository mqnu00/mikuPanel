import asyncio
import importlib
from utils.log_util import log
from core import communication
from core.communication import Message

from websockets.server import ServerConnection


def execute(component_name: str, share: Message):
    communication.share = share
    log.info(component_name)
    module = importlib.import_module(f'components.{component_name}.main')
    component_class = getattr(module, f'{component_name}Component')
    component_instance = component_class()
    component_instance.handle()
    return True
