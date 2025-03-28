import asyncio
import importlib
import json
import os
import pathlib
import pprint

import yaml

from core import communication
from core.communication import Message
from utils.log_util import log
import env_loader

menu_msg: Message = None
menu_role = 0
component_config_file = pathlib.Path(env_loader.BACKEND_PATH) / "componentConfig.yaml"


def init_component():
    communication.ctx.clear()
    # 加载基础组件
    with open(component_config_file, 'r') as f:
        import yaml
        data: dict = yaml.safe_load(f)
    if data:
        for k, v in data.items():
            communication.ctx[k] = v
    # 加载开发组件
    component_dev_path = pathlib.Path(env_loader.BACKEND_PATH) / "components"
    for path in component_dev_path.iterdir():
        if not path.is_dir():
            continue
        if path.name == '__pycache__':
            continue
        # if path.name not in ['']:
        #     continue
        yaml_file = path / f"{path.name}.yaml"
        if not yaml_file.exists():
            continue
        with open(yaml_file, "r") as f:
            data: dict = yaml.safe_load(f)
            print(data)
        for k, v in data.items():
            communication.ctx[k] = v


def set_component(component_name, config):
    with open(component_config_file, 'r+') as f:
        print(component_config_file)
        base_content: dict = yaml.safe_load(f)
        if not base_content:
            base_content = {}
        print(base_content)
        base_content[component_name] = config
        print(base_content)
        f.seek(0)
        f.truncate()
        yaml.dump(base_content, f, sort_keys=False, allow_unicode=True)


def refresh_menu():
    res = [{
        "name": cp_name,
        **cp
    } for cp_name, cp in communication.ctx.items()]
    menu_msg.write(json.dumps(res), menu_role)


def read_component_config(component_name):
    with open(component_config_file, 'r') as f:
        import yaml
        data: dict = yaml.safe_load(f)
    return data[component_name]


def del_component(component_name):
    with open(component_config_file, 'r+') as f:
        print(component_config_file)
        base_content: dict = yaml.safe_load(f)
        if component_name in base_content:
            del base_content[component_name]
        f.seek(0)
        f.truncate()
        yaml.dump(base_content, f, sort_keys=False, allow_unicode=True)


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

    refresh_menu()

    log.info('base menu')

    async def recv():
        # todo 唯一服务
        while True:
            if menu_component_msg.is_ready('recv', menu_component_role):
                info: dict = await menu_component_msg.read(menu_component_role, is_sync=False)
                log.info(info)
                do_info = info.get('do', None)
                if do_info == 'SetComponent':
                    set_component(info["name"], info["config"])
                    init_component()
                    refresh_menu()
                elif do_info == "DelComponent":
                    import env_loader
                    front_path = pathlib.Path(env_loader.FRONTEND_PATH)
                    backend_path = pathlib.Path(env_loader.BACKEND_PATH)
                    component_name = info["name"]
                    component_info: dict = read_component_config(component_name)
                    file_manager = importlib.import_module("components.fileManager.fileManager")
                    # 前端文件处理
                    file_manager.del_path((front_path / component_info["frontend"]).parent)
                    # 后端文件处理
                    file_manager.del_path((
                                                  backend_path / "/".join(
                                              component_info["backend"].split('.')
                                          )).parent)
                    # 配置文件处理
                    del_component(component_name)
                    init_component()
                    refresh_menu()
                    log.info(communication.ctx)
                elif do_info == "close":
                    log.info("menu close")
                    global menu_msg
                    await menu_msg.write(None, menu_role, is_sync=False)
                    return
                else:
                    log.info(info)
                    init_component()
                    refresh_menu()
            else:
                await asyncio.sleep(0)

    loop.run_until_complete(recv())


if __name__ == '__main__':
    # init_component()
    set_component("file", {
        "menu": {

            "label": "文件管理",
            "key": "go-to-file",
            "path": "/file",

        },
        "router": {
            "path": "/file",
            "name": "FileManager",
            "component": "/src/views/fileManager/FileManager.vue"
        }
    })
