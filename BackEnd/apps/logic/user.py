from typing import Optional

from fastapi import Cookie, Depends, Header
from sqlalchemy.orm import Session

from apps.a_common.db import get_session
from apps.a_common.error import PermissionError
from apps.a_common.jwt import decode_token
from apps.crud.user import get_user_with_permission_and_group_by_id
from apps.model.user import UserDB
from utils.time import timer


def get_user_id(token: Optional[str] = Cookie("", alias='user-token', title="用户token", description="推荐通过登录的方式来获得登录凭证（存在cookies中），之后这里就不需要填了"
                                                                                                   "如果想换一个用户（比如换成没权限的用户），可以通过游览器删除token"),
                authorization: Optional[str] = Header("", alias='Authorization')
                ) -> int:
    user_id, ok = decode_token(token or authorization)
    if not ok:
        raise PermissionError()
    return user_id


@timer
def get_user(user_id: int = Depends(get_user_id), session: Session = Depends(get_session)) -> UserDB:
    user = get_user_with_permission_and_group_by_id(session, user_id)
    return user
