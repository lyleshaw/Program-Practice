from sqlalchemy import Column, Index, Integer

from apps.a_common.db import Base


class User2RoleDB(Base):
    __tablename__ = 'user2role'
    __table_args__ = (
        Index('user_id2role_id_index', 'user_id', 'role_id'),
    )
    
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer, nullable=False)
    role_id = Column(Integer, nullable=False)
