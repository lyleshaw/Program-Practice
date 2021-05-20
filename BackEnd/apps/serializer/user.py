from pydantic import BaseModel

from apps.a_common.constants import SEX_LITERAL
from apps.a_common.scheme import PhoneField
from apps.model.user import UserDB


class BaseUserSerializer(BaseModel):
    id: int = None
    name: str
    sex: SEX_LITERAL
    phone: str = PhoneField
    user_identity: int = 0
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example":
                {
                    "sex": 1,
                    'name': '张三',
                    "password": "123123",
                    "phone": "13218655818",
                }
        }


def to_UserDetailSerializer(user: UserDB) -> dict:
    s = UserDetailSerializer.from_orm(user)
    return s.dict()


class UserDetailSerializer(BaseUserSerializer):
    address: str = ''
    nation: int = None
    birthday: int = None
    
    class Config:
        orm_mode = True


class UserUpdateSerializer(BaseModel):
    address: str = ''
    phone: str = PhoneField
    sex: SEX_LITERAL
    nation: int = None
    birthday: int = None


class ManagerUpdateUserSerializer(UserUpdateSerializer):
    name: str


class CreateUser(BaseUserSerializer):
    password: str
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example":
                {
                    "sex": 1,
                    'name': '小明',
                    "password": "123123",
                    "phone": "13218655818",
                }
        }


class ManagerCreateUser(CreateUser):
    password: str = ''
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example":
                {
                    "sex": 1,
                    'name': '小明',
                    "password": "",
                    "phone": "13218655818",
                }
        }


class LoginSerializer(BaseModel):
    phone: str = PhoneField
    password: str
    
    class Config:
        schema_extra = {
            "example":
                {
                    "phone": "17366637777",
                    "password": "123123"
                }
        }
