import asyncio

import sqlalchemy.engine
from sqlalchemy import Column, Integer, DateTime, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, registry

import components.databaseManager.main


class SSHInfo:
    __tablename__ = 'SSHInfo'
    __table_args__ = {'extend_existing': True}

    def __init__(self, host: str, username: str, password: str, port: int = 22, id = None):
        if id:
            self.id = id
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    id = Column(Integer, primary_key=True)
    host = Column(String(length=30))
    port = Column(Integer)
    username = Column(String(length=30))
    password = Column(String(length=128))

    @staticmethod
    def select_all(session: Session):
        """
        查询数据库中所有的 SSHInfo 记录。

        :param session: SQLAlchemy 的异步会话对象
        :return: 包含所有 SSHInfo 对象的列表
        """
        # 构造查询语句
        query = select(SSHInfo)
        result = session.execute(query)
        # 获取所有结果
        ssh_info_list = result.scalars().all()
        return [
            ssh_info.to_dict()
            for ssh_info in ssh_info_list
        ]

    @staticmethod
    def select_by_id(session: Session, id: int):
        """
        根据 ID 查询数据库中的 SSHInfo 记录。

        :param session: SQLAlchemy 的异步会话对象
        :param id: 要查询的 SSHInfo 记录的 ID
        :return: 查询到的 SSHInfo 对象，如果未找到则返回 None
        """
        # 构造查询语句
        query = select(SSHInfo).where(SSHInfo.id == id)
        result = session.execute(query)
        # 获取查询结果
        ssh_info = result.scalars().first()
        return ssh_info.to_dict()

    def to_dict(self):
        """
        将 SSHInfo 对象序列化为字典。

        :return: 包含 SSHInfo 对象属性的字典
        """
        return {
            'id': self.id,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典反序列化为 SSHInfo 对象。

        :param data: 包含 SSHInfo 属性的字典
        :return: SSHInfo 对象
        """
        return cls(
            host=data['host'],
            username=data['username'],
            password=data['password'],
            port=data.get('port', 22)  # 默认端口为 22
        )


if __name__ == '__main__':
    from components.databaseManager.databaseManager import DatabaseManager

    database_manager = DatabaseManager(username='root', password='123456')
    database_manager.mapper_registry.map_declaratively(SSHInfo)
    loop = asyncio.get_event_loop()

    # async def main():
    #     result = await SSHInfo.select_by_id(database_manager.get_async_session(), 1)
    #     print(result)

    # loop.run_until_complete(main())

    print(SSHInfo.select_by_id(database_manager.get_session(), 1))
