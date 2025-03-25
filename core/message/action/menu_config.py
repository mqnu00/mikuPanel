import asyncio
import json
import os
import pathlib
import pprint

from core import communication
from core.communication import Message
from utils.log_util import log
import env_loader

menu_msg: Message = None
menu_role = 0


def init_component():
    # 加载基础组件
    component_config_file = pathlib.Path(env_loader.BACKEND_PATH) / "componentConfig.yaml"
    with open(component_config_file, 'r') as f:
        import yaml
        data: dict = yaml.safe_load(f)
    for k, v in data.items():
        communication.ctx[k] = v



def refresh_menu():
    res = [{
        "name": cp_name,
        **cp
    } for cp_name, cp in communication.ctx.items()]
    menu_msg.write(json.dumps(res), menu_role)


def execute(share_uid: str):
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
    communication.init_ipc(f"menu-component")
    global menu_msg, menu_role
    menu_component_msg: Message = communication.share.get('menu-component')
    log.info(menu_component_msg)
    menu_msg = communication.share.get(share_uid)
    menu_role = 0
    menu_component_role = 1

    init_component()

    communication.ctx.setdefault("user", {

        "menu": {
            "label": "用户",
            "key": "go-to-user",
            "path": "/user",
        },
        "router": {
            "path": "/user",
            "name": "User",
            "component": "/src/views/user/User.vue"
        },

    })

    communication.ctx.setdefault("component", {
        "menu": {
            "label": "插件装载",
            "key": "go-to-component",
            "path": "/component",
        },
        "router": {
            "path": "/component",
            "name": "Component",
            "component": "/src/views/componentConfig/ComponentConfig.vue"
        }
    })

    # communication.ctx.setdefault("docker", {
    #     "menu": {
    #
    #         "label": "容器管理",
    #         "key": "go-to-docker",
    #         "path": "/docker",
    #
    #     },
    #     "router": {
    #         "path": "/docker",
    #         "name": "DockerManager",
    #         "component": "/src/views/dockerManager/DockerManager.vue"
    #     }
    # })

    refresh_menu()

    log.info('base menu')

    async def recv():
        while True:
            if menu_component_msg.is_ready('recv', menu_component_role):
                info = await menu_component_msg.read(menu_component_role, is_sync=False)
                log.info(info)
                refresh_menu()
            else:
                await asyncio.sleep(0)

    loop.run_until_complete(recv())


if __name__ == '__main__':
    init_component()
