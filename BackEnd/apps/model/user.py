from logging import getLogger
from typing import Set

from sqlalchemy import Boolean, Column, Integer, SMALLINT, text, VARCHAR

from apps.a_common.db import Base
from utils.encode import generate_password_hash, is_right_password
from utils.time import int_timestamp

logger = getLogger(__name__)


class UserDB(Base):
    __tablename__ = 'user'
    
    id = Column(Integer(), primary_key=True)
    phone = Column(VARCHAR(126), server_default='', index=True, unique=True)
    password = Column(VARCHAR(126))
    is_superuser = Column(Boolean, server_default=text('False'))
    create_at = Column(Integer, default=int_timestamp)
    update_at = Column(Integer, default=int_timestamp, onupdate=int_timestamp)
    is_active = Column(Boolean, server_default=text('True'))
    
    name = Column(VARCHAR(126), nullable=False)
    sex = Column(SMALLINT)
    address = Column(VARCHAR(255), server_default='')
    nation = Column(SMALLINT)
    birthday = Column(Integer)
    user_identity = Column(Integer, default=0, server_default='0', comment='用户的身份，仅方便进行查询，不做其他任何用处')
    
    def generate_password_hash(self, pw: str):
        self.password = generate_password_hash(pw)
    
    def is_right_password(self, pw: str) -> bool:
        return is_right_password(pw, self.password)
    
    @property
    def permission_set(self) -> Set[str]:
        if not hasattr(self, '_permission_set'):
            self._permission_set = set()
        return self._permission_set
    
    @permission_set.setter
    def permission_set(self, s: Set[str]):
        self._permission_set = s
    
    @property
    def role_set(self) -> Set[str]:
        if not hasattr(self, '_role_set'):
            self._role_set = set()
        return self._role_set
    
    @role_set.setter
    def role_set(self, s: Set[str]):
        self._role_set = s
    
    @property
    def role_id_set(self) -> Set[str]:
        if not hasattr(self, '_role_id_set'):
            self._role_id_set = set()
        return self._role_id_set
    
    @role_id_set.setter
    def role_id_set(self, s: Set[int]):
        self._role_id_set = s


def __str__(self):
    return f'[User: {self.id}]'


def __repr__(self):
    return self.__str__()
