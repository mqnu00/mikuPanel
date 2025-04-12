import asyncio
import uuid

from components.base_component import BaseComponent
from components.databaseManager.databaseManager import DatabaseManager
from core import communication
from core.communication import Message


# todo sql_service
# todo 状态机管理
class DatabaseManagerComponent(BaseComponent):

    def __init__(self, uid):

        super().__init__(uid)
        self.sql_engine = DatabaseManager(
            username='root',
            password='123456'
        )

    def connect_sql(
            module_name,
            cls_name,
            func,
            *args,
            **kwargs
    ):
        """

        :param module_name: 数据表所在模块
        :param func: 执行函数名
        :param args: 执行函数所需参数
        :param kwargs:
        :return: 绝对路径
        """
        print(args)
        print(kwargs)
        import importlib
        table_module = importlib.import_module(module_name)
        table_cls = getattr(table_module, cls_name)
        table_method = getattr(table_cls, func)
        print(table_module)
        print(table_cls)
        print(table_method)
        return table_method(*args, **kwargs)

    def connect_sql_async(
            self,
            module_name,
            cls_name,
            func,
            *args,
            **kwargs
    ):
        print(args)
        print(kwargs)
        import importlib
        import asyncio
        table_module = importlib.import_module(module_name)
        table_cls = getattr(table_module, cls_name)
        table_method = getattr(table_cls, func)
        print(table_module)
        print(table_cls)
        print(table_method)
        loop = asyncio.get_event_loop()
        result = loop.create_task(table_method(self.sql_engine.get_async_session(), *args, **kwargs))
        return result

    def add_msg(self):

        uid = f'sql-{uuid.uuid1()}'
        communication.share[uid] = Message()
        self.uids.append(uid)
        return uid

    def del_msg(self, uid: str):
        del communication.share[uid]
        self.uids.remove(uid)
        return True if communication.share['sql'].get(uid, None) else False

    def handle(self, share_uid):
        """
        组件线程的数据库通信管道分配
        :return:
        """
        self.sql_engine.sql_async_log.info("sql_handle")
        self.sql_engine.sql_async_log.info(self.uid)
        try:
            self.sql_loop = asyncio.get_event_loop()
        except Exception:
            self.sql_loop = asyncio.new_event_loop()

        self.sql_engine.sql_log.info('set database ctx')

        communication.ctx["databaseManager"]['instance'] = self.sql_engine

        self.sql_engine.sql_log.info(communication.ctx["databaseManager"]['instance'])
        self.sql_engine.sql_log.info(self.sql_engine)
        self.sql_engine.sql_log.info(communication.ctx["databaseManager"])
        self.sql_engine.sql_log.info(id(communication.ctx))

        async def func():

            async def return_msg(msg):
                self.sql_engine.sql_async_log.info(msg)
                uid = msg.get('uid')
                do_info = msg.get('do')

                if msg.get('do') == 'runSql':
                    result = await self.connect_sql_async(msg["package"], msg["table"], msg["method"])
                    self.sql_engine.sql_async_log.info(result)
                    await self.write({
                        "do_return": msg.get("do"),
                        "msg": result
                    }, is_sync=False, uid=uid)
                    self.sql_engine.sql_async_log.info("write runSql success")
                elif do_info == 'config':
                    self.sql_engine.create_table(**msg["data"])

            while True:
                msg = await self.read(is_sync=False)
                if not msg:
                    break
                self.sql_loop.create_task(return_msg(msg))

        self.sql_loop.run_until_complete(func())

    def start(self):
        pass
        # self.sql_loop.create_task(self.handle())


from core.LoopManager import loop_manager

# sql_loop = loop_manager.get_or_add_loop_threadsafe('sql_engine')
# sql_service = DataBaseManagerComponent()

if __name__ == '__main__':
    pass
