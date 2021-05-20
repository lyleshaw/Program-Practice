from sqlalchemy import Column, Integer, VARCHAR

from apps.a_common.db import Base


class RoleDB(Base):
    __tablename__ = 'role'
    
    id = Column(Integer(), primary_key=True)
    name = Column(VARCHAR(126), unique=True)
    parent_id = Column(Integer, nullable=False, server_default='0')
    grand_id = Column(VARCHAR(126), nullable=False, server_default='')
    
    def __str__(self):
        return f'[Role: {self.name}]'
    
    def __repr__(self):
        return self.__str__()
    
    @property
    def grand_id_set(self) -> set:
        return {int(i) for i in self.grand_id.split('|') if i != ''}
