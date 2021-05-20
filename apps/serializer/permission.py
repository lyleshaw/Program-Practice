from pydantic import BaseModel


class PermissionSerializer(BaseModel):
    id: int = None
    name: str
    
    class Config:
        orm_mode = True
