import asyncio
import importlib
import multiprocessing

from components.base_component import BaseComponent
from utils.log_util import log
from core import communication
from core.communication import Message

from websockets.server import ServerConnection


def execute(component_name: str, share: Message):
    try:
        multiprocessing.current_process().name = component_name[0].upper()+component_name[1:]
        communication.share = share
        module = importlib.import_module(f'components.{component_name}.main')
        log.info(module)
        component_class = getattr(module, f'{component_name[0].upper()+component_name[1:]}Component')
        component_instance: BaseComponent = component_class()
        if component_instance.config.is_need_sql:
            log.info(component_instance.config.sql_table)
            from core.sqlEngine import sql_engine
            sql_engine.create_table(
                package=f'components.{component_name}.{component_name}',
                tables=component_instance.config.sql_table
            )
        component_instance.handle()
    except Exception:
        log.exception("run wrong")
    return True
