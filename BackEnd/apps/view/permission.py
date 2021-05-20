from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from apps.a_common.db import get_session, Pagination
from apps.a_common.error import NotFound
from apps.a_common.permission import is_superuser
from apps.a_common.response import error_response, make_paginate_info, success_response
from apps.a_common.scheme import PageInfo, PageInfo_
from apps.crud.permission import add_permission, get_permission_by_id, update_permission_by_id
from apps.logic.user import get_user
from apps.model.permission import PermissionDB
from apps.model.user import UserDB
from apps.serializer.permission import PermissionSerializer

permission_router = APIRouter()
permission_prefix = 'permissions'


@permission_router.get("", summary="权限列表")
@is_superuser
async def permission_list(request: Request, page_info: PageInfo = Depends(PageInfo_), user: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    pagination = Pagination(session.query(PermissionDB), page_info=page_info)
    data = [PermissionSerializer.from_orm(m).dict() for m in pagination.items]
    paginate_info = make_paginate_info(pagination, request)
    return success_response(data, paginate_info)


@permission_router.post("", summary="增加权限")
@is_superuser
async def add_permission_(data: PermissionSerializer, user: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    permission = add_permission(session, data)
    session.commit()
    return success_response(PermissionSerializer.from_orm(permission).dict())


@permission_router.put("/{permission_id}", summary="修改权限")
@is_superuser
async def update_permission_(permission_id: int, data: PermissionSerializer, user: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    permission = update_permission_by_id(session, permission_id, data)
    if permission is None:
        return error_response(NotFound())
    session.commit()
    return success_response(PermissionSerializer.from_orm(permission).dict())


@permission_router.delete("/{permission_id}", summary="删除权限")
@is_superuser
async def del_permission_(permission_id: int, user: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    permission = get_permission_by_id(session, permission_id)
    if permission is None:
        return error_response(NotFound())
    session.delete(permission)
    session.commit()
    return success_response(PermissionSerializer.from_orm(permission).dict())
