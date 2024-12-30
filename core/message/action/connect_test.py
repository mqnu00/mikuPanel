from core.communication import Message
from utils.log_util import log


def execute(component_name: str, share: Message):
    log.info(component_name)
    try:
        share.send_queue.put_nowait('123')
    except Exception:
        log.exception('put fail')
    log.info(share.send_queue)