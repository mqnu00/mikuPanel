import multiprocessing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from utils.log_util import setup_logger

# 创建数据库引擎
engine = create_engine('mysql+pymysql://root:123456@localhost/mikuserver?charset=utf8')

engine_log = setup_logger(
            name='sqlalchemy.engine',
            log_dir=rf'D:\program\python\code\mikuPanelGrpc\logs\sql_engine'
        )

# 创建 Session 工厂
Session = sessionmaker(bind=engine)

# 创建 scoped_session
session_factory = scoped_session(Session)

# 创建基类
Base = declarative_base()


# 定义模型
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


# 创建表
Base.metadata.create_all(engine)


def process_task():
    # 获取独立的 Session
    session = session_factory()
    try:
        # 查询数据
        users = session.query(User).all()
        for user in users:
            print(user.name)

        # 修改数据
        user = session.query(User).first()
        user.name = 'New Name'
        session.commit()
    except Exception as e:
        session.rollback()
        print(str(e))
    finally:
        session.close()


if __name__ == '__main__':
    # 创建多个进程
    processes = []
    for _ in range(5):
        p = multiprocessing.Process(target=process_task)
        p.start()
        processes.append(p)

    # 等待所有进程完成
    for p in processes:
        p.join()