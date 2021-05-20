from sqlalchemy import Column, Integer

from apps.a_common.db import Base


class Permission2RoleDB(Base):
    __tablename__ = 'permission2role'
    
    id = Column(Integer(), primary_key=True)
    permission_id = Column(Integer, nullable=False)
    role_id = Column(Integer, nullable=False)
