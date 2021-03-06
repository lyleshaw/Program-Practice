from pydantic import BaseModel


class User2Role(BaseModel):
    user_id: int
    role_id: int
    
    class Config:
        orm_mode = True
