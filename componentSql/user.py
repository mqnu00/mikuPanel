from __future__ import annotations
import json
from typing import List

import sqlalchemy
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.exc import IntegrityError

from core.sqlEngine import sql_engine
from sqlalchemy.future import select


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
    async def select_by_username(username):
        print(username)
        async with sql_engine.get_async_session() as session:
            # 使用异步查询
            query = select(UserInfo).filter(UserInfo.username == username)
            result = await session.execute(query)
            user = result.scalars().first()
            return user

    @staticmethod
    async def register(username, password):
        userinfo = UserInfo(username=username, password=password)
        async with sql_engine.get_async_session() as session:
            try:
                session.add(userinfo)
                await session.commit()  # 异步提交
                await session.refresh(userinfo)  # 异步刷新
                sql_engine.sql_log.info(f"Created user: {userinfo}")
                return userinfo  # 返回创建的用户对象
            except IntegrityError as e:
                sql_engine.sql_log.exception(e)
                return False

    @staticmethod
    async def del_user(username):
        # 异步查询用户对象
        userinfo = await UserInfo.select_by_username(username)
        if userinfo is None:
            sql_engine.sql_log.info(f"User not found: {username}")
            return False  # 用户不存在，返回 False

        async with sql_engine.get_async_session() as session:
            try:
                # 删除指定的用户对象
                await session.delete(userinfo)
                await session.commit()
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
    # userinfo = UserInfo(username='123', password='123')
    # userinfo.create_user(username='456', password='123')
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(UserInfo().del_user('123'))
