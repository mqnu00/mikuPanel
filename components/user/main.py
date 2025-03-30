import asyncio
import json
import time

from components.base_component import BaseComponent
from core import communication
from core.communication import Message


class UserComponent(BaseComponent):

    def __init__(self, uid):

        super().__init__(uid)

    def handle(self, share_uid):
        """

        :param share_uid: 和ws通信用的管道
        :return:
        """
        async def recv():
            user_msg: Message = communication.share.get(share_uid)
            role = 0
            while True:
                if user_msg.is_ready(role=role, check='recv'):

                    msg: dict = json.loads(await user_msg.read(is_sync=False, role=role))
                    if msg.get('username') == '111':
                        communication.allow_router = True
                    else:
                        await user_msg.write(None, role, is_sync=False)
                        return
                    menu_msg: Message = communication.share.get('menu-component')

                    communication.ctx.setdefault("terminal", {
                        "menu": {

                            "label": "终端",
                            "key": "go-to-work",
                            "path": "/terminal",

                        },
                        "router": {
                            "path": "/terminal",
                            "name": "Terminal",
                            "component": "/src/views/terminal/TerminalView.vue"
                        }
                    })



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
        from utils.log_util import log
        log.info("user close")
        # from components.user.user import UserInfo
        # from utils.log_util import log
        # from core import communication
        #
        # # add user_sql_queue
        # user_sql_role = 1
        # sql_do = {
        #     'do': 'add'
        # }
        # sql_msg: Message = communication.share.get('sql')
        # sql_msg.write(content=sql_do, role=1)
        # uid = sql_msg.read(role=1)
        # log.info(uid)
        #
        # # 创建数据表
        # sql_msg.write(
        #     role=user_sql_role,
        #     content={
        #         'do': 'create_table',
        #         'data': {
        #             'package': 'user',
        #             'tables': self.config.sql_table
        #         }
        #     }
        # )
        #
        # user_sql_msg: Message = communication.share.get(uid)
        #
        # # msg = communication.share.recv_queue.get()
        # # username = json.loads(msg).get('name')
        # user_msg: Message = communication.share[share_uid]
        # log.info(user_msg)
        # msg = user_msg.read(0)
        # log.info(msg)
        # # 前端没有传递消息，直接关闭ws
        # if not msg:
        #     log.info('user close')
        #     return True
        # # 执行任务
        # msg = json.loads(msg)
        # # {
        # #     "do": "register",
        # #     "data": {
        # #         "username": "l1",
        # #         "password": "123456"
        # #     }
        # # }
        # # module_name: Any,
        # # cls_name: Any,
        # # func: Any
        # # todo login register 行为验证
        # # 用户注册登录行为 提交给数据库线程操作
        # request_content = dict()
        # request_content['module_name'] = 'user'
        # request_content['cls_name'] = 'UserInfo'
        # request_content['func'] = msg.get('do')
        # request_content.update(msg.get('data'))
        # log.info(request_content)
        # user_sql_msg.write(content=request_content, role=user_sql_role)
        # result = user_sql_msg.read(role=user_sql_role)
        # log.info(result)
        #
        # # userinfo = UserInfo.select_by_username(username)
        # # communication.share.send_queue.put(str(userinfo))
