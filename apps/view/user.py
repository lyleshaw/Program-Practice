from logging import getLogger

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from apps.a_common.db import get_session
from apps.a_common.error import WrongPassword
from apps.a_common.jwt import encode_token
from apps.a_common.response import error_response, success_response
from apps.crud.user import add_user, get_user_by_phone_number, delete_user_by_id
from apps.logic.user import get_user, get_user_id
from apps.model.user import UserDB
from apps.serializer.user import BaseUserSerializer, CreateUser, LoginSerializer, UserUpdateSerializer, to_UserDetailSerializer

user_router = APIRouter()
user_prefix = 'users'
logger = getLogger(__name__)


@user_router.post("/register", summary="注册")
async def register(user_data: CreateUser, session: Session = Depends(get_session)):
    user = add_user(session, user_data)
    session.commit()
    return success_response(to_UserDetailSerializer(user))


@user_router.post("/login", summary="登录")
async def login_(login_data: LoginSerializer, session: Session = Depends(get_session)):
    logger.info(f"phone number: {login_data.phone} login")
    user = get_user_by_phone_number(session=session, phone_number=login_data.phone)
    logger.info(f'get user: {user}')
    if user is None or not user.is_right_password(login_data.password):
        return error_response(WrongPassword())
    data = to_UserDetailSerializer(user)
    user_token = encode_token(user.id).decode()
    data['user_token'] = user_token
    response = success_response(data)
    response.set_cookie('user-token', user_token)
    return response


@user_router.get("/me", summary="获取个人信息")
async def read_self_(user: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    return success_response(to_UserDetailSerializer(user))


@user_router.put("/me", summary="更新用户的数据，所有的字段都需要传递")
async def update_me_(user_data: UserUpdateSerializer, user: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    user.sex = user_data.sex
    user.phone = user_data.phone
    user.address = user_data.address
    user.nation = user_data.nation
    user.birthday = user_data.birthday
    session.add(user)
    session.commit()
    return success_response(to_UserDetailSerializer(user))


@user_router.post("/reset-password", summary="重置密码")
async def reset_password(pw: str = Body(...), user: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    user.generate_password_hash(pw)
    session.add(user)
    session.commit()
    return success_response(BaseUserSerializer.from_orm(user).dict())


@user_router.delete("/delete", summary="注销用户")
async def read_user_by_id_(user_id: int = Depends(get_user_id), session: Session = Depends(get_session)):
    delete_user_by_id(session=session, user_id=user_id)
    session.commit()
    return success_response()
