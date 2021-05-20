from pydantic import BaseModel


class Permission2RoleSerializer(BaseModel):
    permission_id: int
    role_id: int
    
    class Config:
        orm_mode = True
