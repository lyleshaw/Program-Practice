from logging import getLogger
from typing import List

from fastapi import APIRouter, Body, Depends, Query, Request
from sqlalchemy.orm import Session

from apps.a_common.db import get_session, Pagination
from apps.a_common.error import NotFound, PermissionError
from apps.a_common.permission import has_permission_decorator, has_permission_manage_user
from apps.a_common.response import error_response, make_paginate_info, success_response
from apps.a_common.scheme import CommonlyUsedUserSearch, CommonlyUsedUserSearch_, PageInfo, PageInfo_
from apps.crud.user import add_user, get_user_by_id, get_users_by_id_list, common_user_search_with_permission_check
from apps.logic.user import get_user
from apps.model.user import UserDB
from apps.model.user2role import User2RoleDB
from apps.serializer.user import BaseUserSerializer, ManagerCreateUser, to_UserDetailSerializer, ManagerUpdateUserSerializer

manage_user_router = APIRouter()
manage_user_prefix = 'manage-user'
logger = getLogger(__name__)


@manage_user_router.get('/ids', summary="搜索用户的id")
async def search_user_ids(sex: int = Query(None, ge=1, le=2),
                          keyword: str = None,
                          manager: UserDB = Depends(get_user),
                          session: Session = Depends(get_session)
                          ):
    query = session.query(UserDB.id)
    if sex:
        query = query.filter(UserDB.sex == sex)
    if keyword:
        query = query.filter(UserDB.name.ilike(f'%{keyword}%'))
    
    data = [int(i[0]) for i in query.all()]
    return success_response(data)


@manage_user_router.get('', summary="管理员搜索用户")
async def search_user_(request: Request,
                       page_info: PageInfo = Depends(PageInfo_),
                       search_condition: CommonlyUsedUserSearch = Depends(CommonlyUsedUserSearch_),
                       manager: UserDB = Depends(get_user),
                       session: Session = Depends(get_session)
                       ):
    query = session.query(UserDB).join(User2RoleDB, User2RoleDB.user_id == UserDB.id)
    query, error = common_user_search_with_permission_check(manager, query, session, search_condition)
    if error:
        return error_response(error)
    
    paginate = Pagination(query, page_info=page_info)
    paginate_info = make_paginate_info(paginate, request)
    data = [BaseUserSerializer.from_orm(op_user).dict() for op_user in paginate.items]
    return success_response(data, paginate_info)


@manage_user_router.get("/{op_user_id}", summary="管理员获取个人信息")
async def read_op_user_(op_user_id: int, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    op_user = get_user_by_id(session, op_user_id)
    if op_user is None:
        return error_response(NotFound("没找到该用户~"))
    if not has_permission_manage_user(manager, op_user):
        return error_response(PermissionError())
    
    return success_response(to_UserDetailSerializer(op_user))


@manage_user_router.put("/{op_user_id}", summary="管理更新用户的数据，所有的字段都需要传递，除了id")
async def update_op_user_(op_user_id: int, user_data: ManagerUpdateUserSerializer, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    op_user = get_user_by_id(session, op_user_id)
    if not has_permission_manage_user(manager, op_user):
        return error_response(PermissionError())
    
    op_user.sex = user_data.sex
    op_user.phone = user_data.phone
    op_user.address = user_data.address
    op_user.nation = user_data.nation
    op_user.birthday = user_data.birthday
    op_user.name = user_data.name
    session.commit()
    return success_response(to_UserDetailSerializer(op_user))


@manage_user_router.post("", summary="管理员创建用户")
@has_permission_decorator('create-user')
async def manager_create_user(user_data: ManagerCreateUser, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    user = add_user(session, user_data)
    session.commit()
    return success_response(to_UserDetailSerializer(user))


@manage_user_router.post("/reset-password", summary="管理员重置用户密码为123456789")
async def manage_reset_password(op_user_id_list: List[int] = Body(...), manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    op_user_line = get_users_by_id_list(session, op_user_id_list)
    for op_user in op_user_line:
        if not has_permission_manage_user(manager, op_user):
            return error_response(PermissionError())
        op_user.generate_password_hash('123456789')
    session.commit()
    return success_response({'count': len(op_user_line)})
