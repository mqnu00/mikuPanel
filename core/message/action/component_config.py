import asyncio
import importlib
import json
import os
import pathlib
from utils.log_util import log
import pprint
import uuid

import yaml
from aiohttp import web

from core import communication
from core.communication import Message


menu_component_msg: Message = None
component_config_msg: Message = None
component_config_role = 0
menu_component_role = 0


async def read_component_config():
    return json.loads(await component_config_msg.read(component_config_role, is_sync=False))


async def send_component_config(msg):
    return await component_config_msg.write(
        json.dumps(msg) if msg else msg,
        component_config_role,
        is_sync=False
    )


async def save_plugin(request: web.Request):
    reader = await request.multipart()
    while True:
        part = await reader.next()
        if part is None:
            break
        if part.filename:
            # 创建保存路径
            save_path = os.path.join("/home/lzh/program/py-code/mikuPanel/uploads", part.filename)
            log.info(save_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            # 保存文件
            with open(save_path, 'wb') as f:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
            return web.json_response({
                "status": True,
                "compressFile": save_path,
                "msg": f"File {part.filename} uploaded successfully"
            })
        else:
            return web.Response(text="No file uploaded")

def execute(share_uid: str):
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
    communication.init_ipc(f"component-config")
    global component_config_msg, menu_component_msg
    component_config_msg = communication.share.get(share_uid)
    log.info(component_config_msg)
    menu_component_msg = communication.share.get('menu-component')

    log.info('component-config')

    async def install_component(compress_filepath):
        from utils import compress_util
        import env_loader


        compress_filepath = pathlib.Path(compress_filepath)
        component_name = compress_filepath.name.split('.')[0]

        # 解压 组件压缩包
        target_dirpath = pathlib.Path(env_loader.BACKEND_PATH) / "plugins" / component_name
        compress_util.extract_tar_gz(compress_filepath, target_dirpath)

        # 读取组件配置
        with open(target_dirpath / f"{component_name}.yaml", 'r') as f:
            component_info = yaml.safe_load(f)

        # 获取file_manager util
        file_component = communication.ctx.get('FileManager', None)
        if not file_component:
            return {
                "do_return": "install",
                "status": False,
                "info": "no file manager",
                "name": component_name
            }
        # file_component.get("util")
        file_manager = importlib.import_module("components.fileManager.fileManager")
        # 移动前端文件
        frontend_plugin_path = pathlib.Path(env_loader.FRONTEND_PATH) / "plugins" / component_name
        frontend_files = target_dirpath / "frontend"
        for path in frontend_files.iterdir():
            if not path.is_file():
                continue
            file_manager.mv_path(path, frontend_plugin_path)
        # 移动后端文件
        backend_plugin_path = pathlib.Path(env_loader.BACKEND_PATH) / "plugins" / component_name
        backend_files = target_dirpath / "backend"
        for path in backend_files.iterdir():
            if not path.is_file():
                continue
            file_manager.mv_path(path, backend_plugin_path)

        global menu_component_msg
        await menu_component_msg.write({
            "do": "SetComponent",
            "name": component_name,
            "config": component_info[component_name]
        }, menu_component_role, is_sync=False)

        return {
            "do_return": "install",
            "status": True,
            "name": component_name
        }

    async def uninstall_component(component_name):
        global menu_component_msg
        await menu_component_msg.write({
            "do": "DelComponent",
            "name": component_name
        }, menu_component_role, is_sync=False)
        return

    async def recv():
        while True:
            msg: dict = await read_component_config()
            do_info = msg.get("do", None)
            from utils.log_util import log
            log.info(msg)
            if do_info == "install":
                await send_component_config(await install_component(msg["compressFile"]))
            elif do_info == 'uninstall':
                await uninstall_component(msg["component"])
            elif do_info == 'close':
                from utils.log_util import log
                log.info("component config clos")
                await send_component_config(None)
                return







    loop.run_until_complete(recv())


if __name__ == '__main__':
    pass
