import asyncio
import importlib
import multiprocessing
import sys
import threading

from components.base_component import BaseComponent
from utils.log_util import log
from core import communication
from core.communication import Message


def execute(component_name: str, share_uid: str):
    try:
        threading.current_thread().name = component_name[0].upper()+component_name[1:]
        module = importlib.import_module(f'components.{component_name}.main')
        log.info(module)
        component_class = getattr(module, f'{component_name[0].upper()+component_name[1:]}Component')
        component_instance: BaseComponent = component_class(share_uid)
        # if component_instance.config.is_need_sql:
        #     log.info(component_instance.config.sql_table)
            # sql_engine.create_table(
            #     package=f'components.{component_name}.{component_name}',
            #     tables=component_instance.config.sql_table
            # )
        component_instance.handle(share_uid)
    except Exception:
        log.exception("run wrong")
    finally:
        try:
            modules_to_delete = [name for name in sys.modules if name.startswith(component_name)]

            for module_name in modules_to_delete:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    log.info(f"已删除模块: {module_name}")
        except Exception as e:
            log.exception(e)
    return True
