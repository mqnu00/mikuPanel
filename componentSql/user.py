from __future__ import annotations
import json
from typing import List

import sqlalchemy
from sqlalchemy import Column, Integer, String, text
from core.sqlEngine import sql_engine


class UserInfo(sql_engine.SqlBase):
    __tablename__ = 'UserInfo'

    id = Column(Integer, primary_key=True)
    username = Column(String(length=30), unique=True)
    password = Column(String(length=128))

    def __init__(self,
                 id=None,
                 username=None,
                 password=None):
        super().__init__()
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<{self.__class__}(id={self.id}, username={self.username}, password={self.password})>"

    def __str__(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def is_user_exist(userinfo: UserInfo):
        return UserInfo.select_by_username(userinfo.username)

    @staticmethod
    def select_by_username(username):
        with sql_engine.get_session() as session:
            res = session.query(UserInfo).filter(UserInfo.username == username).first()
            return res

    @staticmethod
    def create_user(userinfo: UserInfo):
        with sql_engine.get_session() as session:
            try:
                session.add(userinfo)
                session.commit()
                # 可选：刷新会话以获取数据库生成的值（如自动递增的ID）
                session.refresh(userinfo)
                sql_engine.sql_log.info(f"Created user: {userinfo}")
                return userinfo  # 可选返回创建的用户对象
            except sqlalchemy.exc.IntegrityError as e:
                sql_engine.sql_log.exception(e)
                return False

    @staticmethod
    def del_user(userinfo: UserInfo):
        userinfo = userinfo.select_by_username(userinfo.username)
        with sql_engine.get_session() as session:
            try:

                # 删除指定的用户对象
                session.delete(userinfo)
                session.commit()
                sql_engine.sql_log.info(f"Deleted user: {userinfo}")
                return True  # 返回 True 表示删除成功
            except Exception as e:
                # 如果删除失败，记录异常并返回 False
                sql_engine.sql_log.exception(e)
                return False

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password
        }


if __name__ == '__main__':
    from sqlalchemy import select
    import asyncio


    async def get_users():
        async with sql_engine.get_async_session() as session:
            async with session.begin():
                # 构建查询语句
                query = select(UserInfo).filter(UserInfo.username == 'mqnu00')
                # 执行查询
                result = await session.execute(query)
                # 解析结果
                users = result.scalars().all()
                for user in users:
                    print(user)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_users())

    print(UserInfo.select_by_username('mqnu00'))

