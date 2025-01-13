import importlib

from sqlalchemy import create_engine
from sqlalchemy.orm import Query, declarative_base, DeclarativeBase
from multiprocessing.managers import SyncManager
from core import communication


class SqlEngine(object):

    def __init__(self,
                 username: str,
                 password: str):
        self._init_sql_engine(
            username=username,
            password=password
        )
        self._init_communication(communication.manager)
        pass

    def _init_communication(self,
                            manager: SyncManager):
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

    def create_table(self, table: str):
        importlib.import_module(table)
        self.SqlBase.metadata.create_all(bind=self.sql_engine)

    def search(self):
        pass

    def insert(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


def create_table():
    communication.SqlBase.metadata.create_all(bind=communication.sql_engine)


def search(query: Query):
    from sqlalchemy.orm import sessionmaker
    from components.terminal.terminal import SSHInfo

    # 创建会话类
    Session = sessionmaker(bind=communication.sql_engine)
    session = Session()

    # 查询所有用户
    return query.all()


if __name__ == '__main__':
    from utils.log_util import log, setup_logger

    communication.init_sql(4)
    log.info(communication.SqlBase)
    from components.terminal.terminal import SSHInfo

    create_table()
    search()
