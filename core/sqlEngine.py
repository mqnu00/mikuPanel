import importlib
import logging
import multiprocessing
from multiprocessing.pool import Pool

from sqlalchemy.exc import InvalidRequestError, SQLAlchemyError

from utils.log_util import setup_logger
from sqlalchemy import create_engine, Engine, select, Executable, text, insert, Column, Integer, String, Row, inspect
from sqlalchemy.orm import Query, declarative_base, DeclarativeBase, sessionmaker
from multiprocessing.managers import SyncManager
import pymysql


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
            name='sqlalchemy.engine',
            log_dir=rf'D:\program\python\code\mikuPanelGrpc\logs\sql_engine{multiprocessing.current_process().name}'
        )

        self.sql_engine = create_engine(
            f"{sql_type}+{sql_package}://{username}:{password}@{host}/{dbname}?charset={charset}", pool_size=thread_num)

        self.SqlBase: DeclarativeBase = declarative_base()
        self.inspector = inspect(self.sql_engine)

    def _init_session(self,
                      auto_commit=False,
                      auto_flush=False):

        self.session_maker = sessionmaker(autocommit=auto_commit, autoflush=auto_flush, bind=self.sql_engine)

    def create_table(self, package: str, tables: list[str]):
        exist_tables = self.get_tables()
        for table in tables:
            if table in exist_tables:
                self.sql_log.info(f'{table} already exists')
                return
        importlib.import_module(package)
        self.SqlBase.metadata.create_all(bind=self.sql_engine)

    def get_session(self):
        return self.session_maker()

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


sql_engine = SqlEngine(
    username='root',
    password='123456'
)

# def sql_test(session):
#     result = session.execute(text("SELECT * FROM test_2"))
#     print(result)
#
# if __name__ == '__main__':
#     session = sql_engine.get_session()
#     p1 = multiprocessing.Process(target=sql_test, args=(session,))
#     p1.start()
