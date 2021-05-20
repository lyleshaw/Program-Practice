from typing import List

from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.orm import Session

from apps.a_common.constants import UserIdentity
from apps.a_common.db import get_session
from apps.a_common.error import AppError, InvalidParamError, NotFound, PermissionError
from apps.a_common.permission import has_permission_manage_role, is_superuser, has_permission_manage_user_ids
from apps.a_common.response import empty_paginate_response, error_response, make_paginate_info, success_response
from apps.a_common.scheme import PageInfo, PageInfo_
from apps.crud.user import update_user_identity, cancel_user_as_admin_if_no_role
from apps.crud.role import add_permission_to_role, add_role, get_role_by_id, get_role_by_user_id, get_role_under_user, get_users_by_role_id
from apps.logic.user import get_user
from apps.model.permission2role import Permission2RoleDB
from apps.model.user import UserDB
from apps.model.user2role import User2RoleDB
from apps.model.role import RoleDB
from apps.serializer.user import BaseUserSerializer
from apps.serializer.role import RoleSerializer

role_router = APIRouter()
role_prefix = 'role'


def _check_group_exist_and_permission(session: Session, user: UserDB, role_id: int) -> (RoleDB, AppError):
    role = get_role_by_id(session, role_id)
    if role is None:
        return None, NotFound()
    if not has_permission_manage_role(role, user):
        return None, PermissionError()
    return role, None


@role_router.get("", summary="角色列表，！！！这里有对这一系列接口的介绍！！！")
async def role_list(request: Request, page_info: PageInfo = Depends(PageInfo_), manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    """
    role接口仅对外提供：
    1. user查看自己能看到的role
    
    2. user查看以上role内的user
    
    3. user将自己能管理的user，加到自己能看到的role
    
    4. user将自己能管理的user，从自己能看到的role中删除
    \f
    """
    if len(manager.role_set) == 0 and not manager.is_superuser:
        return empty_paginate_response()
    
    pagination = get_role_under_user(session, manager, page_info=page_info)
    data = [RoleSerializer.from_orm(m).dict() for m in pagination.items]
    paginate_info = make_paginate_info(pagination, request)
    return success_response(data, paginate_info)


@role_router.get("/search", summary="查看某个人属于哪些角色")
async def my_roles(user_id: int, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    has_permission, user_ids = has_permission_manage_user_ids(session, manager, [user_id])
    if not has_permission and not user_id == manager.id:
        return error_response(PermissionError())
    role_list = get_role_by_user_id(session, user_id)
    data = [RoleSerializer.from_orm(role).dict() for role in role_list]
    return success_response(data)


@role_router.get("/{role_id}/users", summary="角色详情，即这个角色下有哪些用户", description="查看的group必须要小于等于自己的group")
async def role_user_list(request: Request, role_id: int, page_info: PageInfo = Depends(PageInfo_), manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role, err = _check_group_exist_and_permission(session, manager, role_id)
    if err is not None:
        return error_response(err)
    
    pagination = get_users_by_role_id(session, role_id, page_info)
    data = [BaseUserSerializer.from_orm(u).dict() for u in pagination.items]
    paginate_info = make_paginate_info(pagination, request)
    return success_response(data, paginate_info)


@role_router.put("/{role_id}", summary="修改角色的名字", description="修改的group必须要小于等于自己的group")
async def update_role_(role_id: int, data: RoleSerializer, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role, err = _check_group_exist_and_permission(session, manager, role_id)
    if err is not None:
        return error_response(err)
    
    role.name = data.name
    if session.query(RoleDB).filter(RoleDB.name == data.name).first() != None:
        return error_response(InvalidParamError("角色名重复！"))
    session.add(role)
    session.commit()
    return success_response(RoleSerializer.from_orm(role).dict())


@role_router.post("/{role_id}/users:add", summary="将用户批量添加到角色")
async def add_user_to_role(role_id: int, user_ids: List[int] = Body(...), manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role, err = _check_group_exist_and_permission(session, manager, role_id)
    if err is not None:
        return error_response(err)
    has_permission, user_ids = has_permission_manage_user_ids(session, manager, user_ids)
    if not has_permission:
        return error_response(PermissionError())
    
    session.add_all(tuple(User2RoleDB(user_id=i, role_id=role_id) for i in user_ids))
    update_user_identity(session, user_ids, UserIdentity.ADMIN)
    session.commit()
    return success_response()


@role_router.post("/{role_id}/users:delete", summary="将用户批量从角色中删除")
async def del_user_to_role(role_id: int, user_ids: List[int], manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role, err = _check_group_exist_and_permission(session, manager, role_id)
    if err is not None:
        return error_response(err)
    has_permission, user_ids = has_permission_manage_user_ids(session, manager, user_ids)
    if not has_permission:
        return error_response(PermissionError())
    
    session.query(User2RoleDB).filter(User2RoleDB.role_id == role_id, User2RoleDB.user_id.in_(user_ids)).delete(False)
    cancel_user_as_admin_if_no_role(session, user_ids)
    session.commit()
    return success_response()


@role_router.post("", summary="增加角色，这个接口不对外开放")
@is_superuser
async def add_role_(data: RoleSerializer, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role = add_role(session, data)
    session.commit()
    return success_response(RoleSerializer.from_orm(role).dict())


@role_router.delete("/{role_id}", summary="删除角色, 同时删除用户的关联信息，这个接口不对外开放")
@is_superuser
async def del_role(role_id: int, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role, err = _check_group_exist_and_permission(session, manager, role_id)
    if err is not None:
        return error_response(err)
    # todo: 这里按道理要递归删除，但是还没做
    session.delete(role)
    session.query(User2RoleDB).filter(User2RoleDB.role_id == role_id).delete(False)
    session.commit()
    return success_response(RoleSerializer.from_orm(role).dict())


@role_router.post("/{role_id}/permission:add", summary="将权限批量添加到角色，这个接口不对外开放")
@is_superuser
async def psot_permission_to_role_(role_id: int, permission_ids: List[int] = Body(...), manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role, err = _check_group_exist_and_permission(session, manager, role_id)
    if err is not None:
        return error_response(err)
    
    add_permission_to_role(session, permission_ids, role_id)
    session.commit()
    return success_response()


@role_router.post("/{role_id}/permission:delete", summary="将权限批量从角色中删除，这个接口不对外开放")
@is_superuser
async def del_permission_to_role(role_id: int, permission_ids: List[int], manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    role, err = _check_group_exist_and_permission(session, manager, role_id)
    if err is not None:
        return error_response(err)
    
    session.query(Permission2RoleDB). \
        filter(Permission2RoleDB.role_id == role_id). \
        filter(Permission2RoleDB.permission_id.in_(permission_ids)).delete(False)
    session.commit()
    return success_response()
