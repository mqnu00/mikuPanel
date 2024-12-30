import importlib
import json
import uuid
from core import communication
from utils.log_util import log


def action_dispatch(msg: str):
    log.info(msg)
    resolve_msg: dict = json.loads(msg)
    component_name = resolve_msg["type"]
    uid = f'{component_name}-{str(uuid.uuid1())}'
    log.info(uid)
    communication.init_ipc(uid)

    module = importlib.import_module('.'.join([resolve_msg['dir'], resolve_msg['module']]))
    result = communication.process_pool.apply_async(func=module.execute,
                                                    args=(component_name, communication.share.get(uid)))
    return uid
