import json
from typing import List

from sqlalchemy import Column, Integer, DateTime, String, select

from core.component_init import Config
from core.sqlEngine import sql_engine


class UserInfo(sql_engine.SqlBase):
    __tablename__ = 'UserInfo'

    id = Column(Integer, primary_key=True)
    username = Column(String(length=30), unique=True)
    password = Column(String(length=128))

    def __repr__(self):
        return f"<{self.__class__}(id={self.id}, username={self.username}, password={self.password})>"

    @staticmethod
    def select_by_username(username):
        with sql_engine.get_session() as session:
            res: List[UserInfo] = session.query(UserInfo).filter(UserInfo.username == username).all()
            sql_engine.sql_log.info(res)
            return res[0]

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password
        }

    def __str__(self):
        return json.dumps(self.to_dict())


class User(object):

    pass
