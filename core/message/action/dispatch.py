import importlib
import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from core import communication
from utils.log_util import log


def run(component_name):
    uid = f'{component_name}-{str(uuid.uuid1())}'
    log.info(uid)
    communication.init_ipc(uid)

    module = importlib.import_module("core.message.action.run")
    log.info(module)

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(module.execute, component_name, uid)

    return uid, future


def action_dispatch(msg: str):
    log.info(msg)

    resolve_msg: dict = json.loads(msg)
    if resolve_msg["type"] == "run":
        # 判断是否需要权限验证
        if not communication.allow_router:
            component_name = 'user'
            return run(component_name)
        else:
            return run(resolve_msg["component"])
    elif resolve_msg["type"] == "menu":
        uid = f'menu-{str(uuid.uuid1())}'
        log.info(uid)
        communication.init_ipc(uid)

        module = importlib.import_module('.'.join([resolve_msg['dir'], resolve_msg['module']]))
        log.info(module)

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(module.execute, uid)

        return uid, future

    elif resolve_msg["type"] == "component-config":
        uid = f'component-config-{str(uuid.uuid1())}'
        log.info(uid)
        communication.init_ipc(uid)

        module = importlib.import_module("core.message.action.component_config")
        log.info(module)

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(module.execute, uid)

        return uid, future

    # return module.execute(component_name, uid)
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     future = executor.submit(module.execute, component_name, uid)  # 提交任务
    # # result = communication.process_pool.apply_async(func=module.execute,
    # #                                                 args=(component_name, communication.share.get(uid)))
    #     log.info("???")
    #     return uid, future
