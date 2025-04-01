import asyncio
import inspect
import json

from docker.errors import DockerException

from components.base_component import BaseComponent
import docker

from components.dockerManager.dockerManager import DockerManager
from core.communication import Message
from core import communication

from utils.log_util import log


class DockerManagerComponent(BaseComponent):

    def __init__(self, uid):

        super().__init__(uid)


    def handle(self, share_uid):

        log.info("docker")

        try:
            self.loop = asyncio.get_event_loop()
        except Exception:
            self.loop = asyncio.new_event_loop()

        async def solve():
            self.docker = DockerManager()
            while True:
                msg: dict = json.loads(await self.read(is_sync=False))
                log.info(msg)
                do_info = msg["do"]

                if do_info == "close":
                    self.write(None)
                    return
                else:
                    method = getattr(self.docker, do_info)
                    if do_info == "close":
                        await self.write(None)
                        return
                    else:
                        method = getattr(self.docker, do_info)
                        if "data" in msg:
                            data = msg["data"]
                        else:
                            data = None
                    self.loop.create_task(run_method(do_info, method, data))

        async def run_method(do_info, method, data):
            try:
                if inspect.iscoroutinefunction(method):
                    if data is not None:
                        res = await method(**data)
                    else:
                        res = await method()
                else:
                    if data is not None:
                        res = method(**data)
                    else:
                        res = method()
                log.info(res)
                await self.write(content=json.dumps({
                    "do_return": do_info,
                    **res
                }), is_sync=False)
            except Exception as e:
                log.error(f"Error running method: {e}")

        self.loop.run_until_complete(solve())
