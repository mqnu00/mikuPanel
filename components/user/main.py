import json

from components.base_component import BaseComponent
from core.component_init import Config


class UserComponent(BaseComponent):

    def __init__(self):
        self.config = Config(
            is_need_sql=True,
            sql_table=['userinfo']
        )

    def handle(self):
        from components.user.user import UserInfo
        from utils.log_util import log
        from core import communication

        # msg = communication.share.recv_queue.get()
        # username = json.loads(msg).get('name')
        username = 'mqnu00'
        log.info(username)
        userinfo = UserInfo.select_by_username(username)
        communication.share.send_queue.put(str(userinfo))
