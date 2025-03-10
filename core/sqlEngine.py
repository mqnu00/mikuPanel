import asyncio
import importlib
import json
import logging
import multiprocessing
import sys
import time
import uuid
from multiprocessing.pool import Pool
from typing import List

from rx.subject import Subject
from sqlalchemy.exc import InvalidRequestError, SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine
from transitions import EventData

from core.service import Service
from utils.log_util import setup_logger
from sqlalchemy import create_engine, Engine, Executable, text, insert, Column, Integer, String, Row, inspect
from sqlalchemy.orm import Query, declarative_base, DeclarativeBase, sessionmaker
from multiprocessing.managers import SyncManager
import pymysql
import aiomysql
from sqlalchemy.ext.asyncio import AsyncSession

from core import communication
from core.communication import Message


# todo 修改为组件
class SqlEngine(object):

    def __init__(self,
                 username: str,
                 password: str):
        self._init_sql_engine(
            username=username,
            password=password
        )
        self._init_session()

    def _init_sql_engine(self,
                         username: str,
                         password: str,
                         sql_type: str = 'mysql',
                         sql_package: str = 'pymysql',
                         dbname: str = 'mikuserver',
                         host: str = 'localhost',
                         charset: str = 'utf8',
                         thread_num: int = 4):

        self.sql_log = setup_logger(
            name='sqlalchemy.engine.Engine.sync_engine',
            log_dir=rf'D:\program\python\code\mikuPanelGrpc\logs\sql_engine{multiprocessing.current_process().name}'
        )
        self.sql_async_log = setup_logger(
            name='sqlalchemy.engine.Engine.async_engine',
            log_dir=rf'D:\program\python\code\mikuPanelGrpc\logs\sql_async_engine{multiprocessing.current_process().name}'
        )

        self.sql_engine = create_engine(
            f"{sql_type}+{sql_package}://{username}:{password}@{host}/{dbname}?charset={charset}", pool_size=thread_num,
            logging_name='sync_engine')
        self.sql_async_engine = create_async_engine(
            f"{sql_type}+aiomysql://{username}:{password}@{host}/{dbname}?charset={charset}",
            logging_name='async_engine')
        # print(self.sql_engine_async.logging_name)

        self.SqlBase: DeclarativeBase = declarative_base()
        self.inspector = inspect(self.sql_engine)

    def _init_session(self,
                      auto_commit=False,
                      auto_flush=False):

        self.session_maker = sessionmaker(autocommit=auto_commit, autoflush=auto_flush, bind=self.sql_engine)
        self.session_maker_async = sessionmaker(autocommit=auto_commit, autoflush=auto_flush,
                                                bind=self.sql_async_engine, class_=AsyncSession)

    def create_table(self, package: str, tables: list[str]):
        exist_tables = self.get_tables()
        for table in tables:
            if table in exist_tables:
                self.sql_log.info(f'{table} already exists')
        importlib.import_module(f'componentSql.{package}')
        self.SqlBase.metadata.create_all(bind=self.sql_engine)

    def get_session(self):
        return self.session_maker()

    def get_async_session(self) -> AsyncSession:
        return self.session_maker_async()

    def get_tables(self):
        return self.inspector.get_table_names()

    def execute(self, query: Executable):

        self.sql_log.info(type(query))

        with self.session_maker() as session:

            result = session.execute(query)

            if query.is_select:

                return result.scalars().all()
            else:

                session.commit()

                if query.is_insert:

                    # self.sql_log.info(result.inserted_primary_key)
                    # self.sql_log.info(type(result.inserted_primary_key))
                    inserted_primary_key: Row = result.inserted_primary_key
                    return inserted_primary_key
                elif query.is_delete:

                    return result.rowcount
                elif query.is_update:

                    return result.rowcount

        # todo sql_service
        def start():
            pass


sql_engine = SqlEngine(
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
        module_name,
        cls_name,
        func,
        *args,
        **kwargs
):
    sql_engine.sql_async_log.info("???")
    print(args)
    print(kwargs)
    import importlib
    import asyncio
    table_module = importlib.import_module(f'componentSql.{module_name}')
    table_cls = getattr(table_module, cls_name)
    table_method = getattr(table_cls, func)
    print(table_module)
    print(table_cls)
    print(table_method)
    loop = asyncio.get_event_loop()
    result = loop.create_task(table_method(*args, **kwargs))
    return result


def read_task_from_pipe():
    msg = communication.share.read(communication.share['sql'])


# class SqlService(Service):
#
#     def __init__(self, loop):
#         super().__init__(loop)
#         self.messages: dict[str, Message] = {}
#         self.is_config = False
#         self.config_obs = Subject()
#         self.config_obs.subscribe(lambda uid: self.config(uid=uid))
#
#     def _config(self, event: EventData):
#         # 浅拷贝
#         # self.messages: dict[str, Message] = communication.share['sql']
#         # for k in self.messages:
#         #     self.messages[k].set_role(1)
#         self.pending()
#
#     def _pending(self, event):
#         for uid, msg in communication.share['sql'].items():
#             msg: Message
#             msg.set_role(1)
#             if msg.is_ready(check='recv'):
#                 result = self.working(msg=msg.read(is_sync=False))
#                 msg.write(result)
#
#     def _working(self, event):
#         msg = event.kwargs.get('msg')
#         msg = json.loads(msg)
#         return connect_sql_async(
#             **msg
#         )


# todo sql_service
# todo 状态机管理
class SqlService(object):

    def __init__(self):
        self.uids = []

    def add_msg(self):

        uid = f'sql-{uuid.uuid1()}'
        communication.share[uid] = Message()
        self.uids.append(uid)
        return uid

    def del_msg(self, uid: str):
        del communication.share[uid]
        self.uids.remove(uid)
        return True if communication.share['sql'].get(uid, None) else False

    async def execute_sql(self, uid):
        """
        具体执行组件所需的sql命令
        调用的sql应当在componentSql包定义好
        :param uid:
        :return:
        """
        sql_msg_role = 0
        sql_msg: Message = communication.share[uid]
        while True:
            if not sql_msg.is_ready('recv', sql_msg_role):
                await asyncio.sleep(0)
            else:
                msg = await sql_msg.read(role=sql_msg_role, is_sync=False)
                sql_engine.sql_async_log.info(msg)
                await connect_sql_async(**msg)

    async def handle(self):
        """
        组件线程的数据库通信管道分配
        :return:
        """
        sql_engine.sql_async_log.info("sql_handle")
        sql_msg_role = 0
        sql_msg: Message = communication.share['sql']
        while True:
            if not sql_msg.is_ready('recv', sql_msg_role):
                await asyncio.sleep(0)
            else:
                msg = await sql_msg.read(role=sql_msg_role, is_sync=False)

                if msg.get('do') == 'add':
                    uid = self.add_msg()
                    await sql_msg.write(uid, role=sql_msg_role, is_sync=False)
                    sql_loop.loop.create_task(self.execute_sql(uid))
                elif msg.get('do') == 'del':
                    await sql_msg.write(self.del_msg(msg.get('uid')), role=sql_msg_role, is_sync=False)
                elif msg.get('do') == 'create_table':
                    sql_engine.sql_async_log.info(msg)
                    sql_engine.create_table(**msg.get('data'))

    def start(self):
        sql_loop.loop.create_task(self.handle())


from core.LoopManager import Loop, loop_manager

sql_loop = loop_manager.get_or_add_loop_threadsafe('sql_engine')
sql_service = SqlService()

if __name__ == '__main__':
    # print(connect_sql('componentSql.user',
    #             'UserInfo',
    #             'select_by_username',
    #             username='mqnu00'))

    # print(connect_sql_async('componentSql.user',
    #             'UserInfo',
    #             'select_by_username',
    #             username='mqnu00'))
    # print(connect_sql_async('componentSql.user',
    #                         'UserInfo',
    #                         'create_user',
    #                         username='4343', password='5656'))
    # sql_service.config_obs.on_next('112233')
    pass
