import asyncio
import json

from components.base_component import BaseComponent
from core.communication import Message
from components.fileManager import fileManager
from core.LoopManager import loop_manager
from core import communication


class FileManagerComponent(BaseComponent):

    def __init__(self, uid):
        super().__init__(uid)

    def handle(self, share_id):

        try:
            self.loop = asyncio.get_event_loop()
        except Exception:
            self.loop = asyncio.new_event_loop()

        file_msg_role = 0
        self.file_msg: Message = communication.share.get(share_id)

        async def resolve():
            from utils.log_util import log
            log.info('on coro')

            while True:
                if not self.file_msg.is_ready('recv', file_msg_role):
                    await asyncio.sleep(0)
                info = await self.file_msg.read(file_msg_role, is_sync=False)
                log.info(info)

                if not info:
                    break

                msg: dict = json.loads(info)
                do_info = msg.get('do')

                if do_info == 'list':
                    # {
                    #     "do": 'list',
                    #     "data": {
                    #         "dir": '/'
                    #     }
                    # }
                    log.info(do_info)
                    res = fileManager.get_file_list(msg.get('data').get('dir'))
                    log.info(res)
                    await self.file_msg.write(json.dumps({
                        "do_return": "list",
                        "data": {
                            "nowPath": res.get("nowPath"),
                            "list": [
                                {
                                    "id": i,
                                    **p.__dict__
                                } for i, p in enumerate(res.get('list'))
                            ]
                        }
                    }), is_sync=False, role=file_msg_role)

                elif do_info == 'openFile':
                    content = fileManager.get_file_content(msg.get('data').get('dir'))
                    await self.file_msg.write(json.dumps({
                        "do_return": 'openFile',
                        "data": {
                            "content": content
                        }
                    }), is_sync=False, role=file_msg_role)

                elif do_info == 'saveFile':
                    fileManager.save_file(
                        msg.get('data').get('dir'),
                        msg.get('data').get('fileContent')
                    )
                    await self.file_msg.write(json.dumps({
                        "do_return": 'saveFile',
                        "data": {
                            "isDone": True
                        }
                    }), is_sync=False, role=file_msg_role)

                elif do_info == 'close':
                    log.info("file close")
                    await self.file_msg.write(None, is_sync=False, role=file_msg_role)
                    break

        self.loop.run_until_complete(resolve())
