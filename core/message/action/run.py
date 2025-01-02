import asyncio
import importlib
import multiprocessing

from utils.log_util import log
from core import communication
from core.communication import Message

from websockets.server import ServerConnection


def execute(component_name: str, share: Message):
    try:
        multiprocessing.current_process().name = component_name[0].upper()+component_name[1:]
        communication.share = share
        log.info(component_name)
        module = importlib.import_module(f'components.{component_name}.main')
        component_class = getattr(module, f'{component_name[0].upper()+component_name[1:]}Component')
        component_instance = component_class()
        component_instance.handle()
    except Exception:
        log.exception("run wrong")
    return True
