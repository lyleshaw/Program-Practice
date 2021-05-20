from logging import getLogger
from typing import List

from sqlalchemy.orm import Session

from apps.a_common.db import or_many_condition, Pagination
from apps.a_common.scheme import PageInfo
from apps.model.permission2role import Permission2RoleDB
from apps.model.user import UserDB
from apps.model.user2role import User2RoleDB
from apps.model.role import RoleDB
from apps.serializer.role import RoleSerializer

logger = getLogger(__name__)


def get_role_by_id(session: Session, i: int) -> RoleDB:
    return session.query(RoleDB).filter(RoleDB.id == i).first()


def get_users_by_role_id(session: Session, i: int, page_info: PageInfo) -> Pagination:
    users = session.query(UserDB). \
        filter(RoleDB.id == i). \
        filter(User2RoleDB.role_id == RoleDB.id). \
        filter(User2RoleDB.user_id == UserDB.id)
    
    pagination = Pagination(users, page_info=page_info)
    return pagination


def get_role_under_user(session: Session, user: UserDB, page_info: PageInfo) -> Pagination:
    if user.is_superuser:
        pagination = Pagination(session.query(RoleDB), page_info=page_info)
        return pagination
    
    query = session.query(RoleDB)
    condition_list = [RoleDB.id.in_(user.role_id_set)]
    for role_id in user.role_id_set:
        condition_list.append(RoleDB.grand_id.like(f'%|{role_id}|%'))
    
    query = query.filter(or_many_condition(condition_list))
    pagination = Pagination(query, page_info=page_info)
    return pagination


def get_role_by_user_id(session: Session, user_id: int) -> List[RoleDB]:
    return session.query(RoleDB).filter(User2RoleDB.user_id == user_id, User2RoleDB.role_id == RoleDB.id).all()


def add_permission_to_role(session: Session, permission_ids: List[int], role_id: int):
    session.add_all(tuple(Permission2RoleDB(permission_id=i, role_id=role_id) for i in permission_ids))


def add_role(session: Session, data: RoleSerializer) -> RoleDB:
    grand_id = ''
    if data.parent_id:
        parent_grand_id = session.query(RoleDB).filter(RoleDB.id == data.parent_id).value(RoleDB.grand_id)
        if parent_grand_id:
            grand_id = f'{parent_grand_id}{data.parent_id}|'
        else:
            grand_id = f'|{data.parent_id}|'
    role = RoleDB(name=data.name, parent_id=data.parent_id or 0, grand_id=grand_id)
    session.add(role)
    return role
