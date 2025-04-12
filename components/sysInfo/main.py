import asyncio
import inspect
import json
import traceback

from components.base_component import BaseComponent
from components.sysInfo.sysInfo import SysInfo
from utils.log_util import log


class SysInfoComponent(BaseComponent):

    def __init__(self, uid):
        super().__init__(uid)

    def handle(self, uid):

        try:
            self.loop = asyncio.get_event_loop()
        except Exception:
            self.loop = asyncio.new_event_loop()

        async def solve():
            self.sysInfo = SysInfo()
            while True:
                msg: dict = json.loads(await self.read(is_sync=False))
                # log.info(msg)
                do_info = msg["do"]

                if do_info == "close":
                    self.write(None)
                    return
                else:
                    method = getattr(self.sysInfo, do_info)
                    if do_info == "close":
                        await self.write(None)
                        return
                    else:
                        method = getattr(self.sysInfo, do_info)
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
                await self.write(content=json.dumps({
                    "do_return": do_info,
                    "data": {
                        **res
                    }
                }), is_sync=False)
            except Exception as e:
                traceback.print_exc()
                log.error(f"Error running method: {e}")

        self.loop.run_until_complete(solve())