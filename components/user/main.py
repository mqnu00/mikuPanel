import asyncio
import json
import time
import uuid

from components.base_component import BaseComponent
from core import communication
from core.communication import Message
from utils.log_util import log


class UserComponent(BaseComponent):

    def __init__(self, uid):

        super().__init__(uid)

    def handle(self, share_uid):
        """

        :param share_uid: 和ws通信用的管道
        :return:
        """

        communication.ctx['user']['verifyTokens'] = []

        async def recv():
            user_msg: Message = communication.share.get(share_uid)
            role = 0
            while True:
                if user_msg.is_ready(role=role, check='recv'):

                    msg: dict = json.loads(await user_msg.read(is_sync=False, role=role))
                    if msg.get('username') == '111':
                        verify_token = str(uuid.uuid1())
                        log.info(verify_token)
                        communication.ctx['user']['verifyTokens'].append(verify_token)
                        self.write(content=verify_token)
                    else:
                        await user_msg.write(None, role, is_sync=False)
                        return
                    menu_msg: Message = communication.share.get('menu-component')



                    await menu_msg.write({
                        "label": "文件管理",
                        "key": "go-to-file",
                        "path": "/file",
                    }, 0, is_sync=False)

                    await user_msg.write(None, role, is_sync=False)
                    return
                else:
                    await asyncio.sleep(0)
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()

        loop.run_until_complete(recv())

        log.info("user close")
