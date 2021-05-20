from sqlalchemy import Column, Integer, VARCHAR

from apps.a_common.db import Base


class PermissionDB(Base):
    __tablename__ = 'permission'
    
    id = Column(Integer(), primary_key=True)
    name = Column(VARCHAR(126), unique=True, nullable=False)
    
    def __str__(self):
        return f'[Permission: {self.name}]'
    
    def __repr__(self):
        return self.__str__()
