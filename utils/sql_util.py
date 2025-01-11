from sqlalchemy.orm import Query

from core import communication


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
    from utils.log_util import log
    communication.init_sql(4)
    log.info(communication.SqlBase)
    from components.terminal.terminal import SSHInfo
    create_table()
    search()
