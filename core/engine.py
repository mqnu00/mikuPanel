from concurrent.futures import Future

from core.message.action import menu_config, dispatch
from core import communication
from utils.log_util import log

menu_config.init_component()
long_services = dict()

for component_name, config in communication.ctx.items():
    msg_id = config.get("msgId", None)
    if msg_id:
        log.info(f"start {component_name}")
        communication.init_ipc(msg_id)
        long_services[component_name] = dispatch.run(component_name, msg_id)[2]


def stop_long_service(component_name):
    future: Future = long_services.get(component_name, None)
    if future:
        try:
            if future.cancel():
                del long_services[component_name]
        except Exception:
            log.exception("持久服务终止失败")
