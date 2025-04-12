import importlib
import multiprocessing

import sqlalchemy
from sqlalchemy import create_engine, Executable, Row, inspect, MetaData, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, DeclarativeBase, sessionmaker, registry

from utils.log_util import setup_logger


# todo 修改为组件
class DatabaseManager(object):

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

        import env_loader

        self.sql_log = setup_logger(
            name='sqlalchemy.engine.Engine.sync_engine',
            log_dir=rf'{env_loader.BACKEND_PATH}/logs/sql_engine{multiprocessing.current_process().name}'
        )
        self.sql_async_log = setup_logger(
            name='sqlalchemy.engine.Engine.async_engine',
            log_dir=rf'{env_loader.BACKEND_PATH}/logs/sql_async_engine{multiprocessing.current_process().name}'
        )

        self.sql_engine = create_engine(
            f"{sql_type}+{sql_package}://{username}:{password}@{host}/{dbname}?charset={charset}", pool_size=thread_num,
            logging_name='sync_engine')
        self.sql_async_engine = create_async_engine(
            f"{sql_type}+aiomysql://{username}:{password}@{host}/{dbname}?charset={charset}",
            logging_name='async_engine')
        # print(self.sql_engine_async.logging_name)

        self.mapper_registry = registry()
        self.SqlBase = self.mapper_registry.generate_base()
        self.inspector = inspect(self.sql_engine)
        self.metadata = MetaData()

    def _init_session(self,
                      auto_commit=False,
                      auto_flush=False):

        self.session_maker = sessionmaker(autocommit=auto_commit, autoflush=auto_flush, bind=self.sql_engine)
        self.session_maker_async = sessionmaker(autocommit=auto_commit, autoflush=auto_flush,
                                                bind=self.sql_async_engine, class_=AsyncSession)

    def create_table(self, package: str, tables: list[str]):
        exist_tables = self.get_tables()
        self.sql_async_log.info(exist_tables)

        for table in tables:
            self.sql_async_log.info(table)
            # if table.lower() in exist_tables:
            #     try:
            #         # 删除原表
            #         existing_table = sqlalchemy.Table(table, metadata, autoload_with=self.sql_engine)
            #         existing_table.drop(self.sql_engine)
            #     except Exception:
            #         self.sql_log.exception(f"table {table} redo wrong")

            module = importlib.import_module(package)
            Table = getattr(module, table)
            # if not table in self.SqlBase.metadata.tables:
            self.mapper_registry.map_declaratively(Table)
            # else:
            #     self.sql_async_log.info(f"Table {table} is already mapped.")
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




if __name__ == '__main__':
    sql_engine = DataBaseManager(
        username='root',
        password='123456'
    )
    sql_engine.sql_async_log.info("???")