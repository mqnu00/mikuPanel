import importlib
import logging
import multiprocessing
from multiprocessing.pool import Pool
from utils.log_util import setup_logger
from sqlalchemy import create_engine, Engine, select, Executable, text, insert, Column, Integer, String, Row
from sqlalchemy.orm import Query, declarative_base, DeclarativeBase, sessionmaker
from multiprocessing.managers import SyncManager


class Message(object):

    def __init__(self):
        self.action_info = manager.dict()
        self.recv_queue = manager.Queue()
        self.send_queue = manager.Queue()


class SqlEngine(object):

    def __init__(self,
                 username: str,
                 password: str):
        self._init_sql_engine(
            username=username,
            password=password
        )
        self._init_session()
        self._init_communication()
        pass

    def _init_communication(self):
        self.send_queue = manager.Queue()
        self.recv_queue = manager.Queue()

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
            log_dir=rf'D:\program\python\code\mikuPanelGrpc\logs\sql_engine'
        )

        self.sql_engine = create_engine(
            f"{sql_type}+{sql_package}://{username}:{password}@{host}/{dbname}?charset={charset}", pool_size=thread_num)

        self.SqlBase: DeclarativeBase = declarative_base()

    def _init_session(self,
                      auto_commit=False,
                      auto_flush=False):

        self.session_maker = sessionmaker(autocommit=auto_commit, autoflush=auto_flush, bind=self.sql_engine)

    def create_table(self, table: str):
        importlib.import_module(table)
        self.SqlBase.metadata.create_all(bind=self.sql_engine)

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


manager: SyncManager = None
share: dict[str, Message] | Message = {}
process_pool: Pool = None
SqlBase: DeclarativeBase = None
sql_engine: SqlEngine = None


def pool_initializer():
    pass


def init_pool(num: int):
    global process_pool
    process_pool = multiprocessing.Pool(num, initializer=pool_initializer, initargs=())


def init_ipc(info: str = None):
    if info:
        global share
        share[info] = Message()
    else:
        # 保证 manager 只有一个
        global manager
        manager = multiprocessing.Manager()


# todo single_sql_process
def init_sql(num: int):

    global sql_engine
    sql_engine = SqlEngine(
        username='root',
        password='123456'
    )


if __name__ == '__main__':

    init_ipc()
    init_sql(4)

    class Test(sql_engine.SqlBase):
        __tablename__ = 'test_2'

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(100), nullable=False)

    sql_engine.execute(insert(
        table=Test
    ).values(name='Alice'))

    sql_engine.execute(text("insert into test_2 (name) values ('123');"))

