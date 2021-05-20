from pydantic import BaseModel


class RoleSerializer(BaseModel):
    id: int = None
    name: str
    parent_id: int = 0
    grand_id: str = ''
    
    class Config:
        orm_mode = True
