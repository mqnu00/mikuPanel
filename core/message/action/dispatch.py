import importlib
import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from core import communication
from utils.log_util import log


def action_dispatch(msg: str):
    log.info(msg)
    resolve_msg: dict = json.loads(msg)
    component_name = resolve_msg["component"]
    uid = f'{component_name}-{str(uuid.uuid1())}'
    log.info(uid)
    communication.init_ipc(uid)

    module = importlib.import_module('.'.join([resolve_msg['dir'], resolve_msg['module']]))
    log.info(module)

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(module.execute, component_name, uid)

    return uid, future

    # return module.execute(component_name, uid)
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     future = executor.submit(module.execute, component_name, uid)  # 提交任务
    # # result = communication.process_pool.apply_async(func=module.execute,
    # #                                                 args=(component_name, communication.share.get(uid)))
    #     log.info("???")
    #     return uid, future
