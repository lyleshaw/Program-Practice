from typing import List, Tuple, Union, Set

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from apps.a_common.constants import USER_IDENTITY_LITERAL, UserIdentity
from apps.a_common.db import fast_count, or_many_condition
from apps.a_common.error import AppError, InvalidParamError, PermissionError
from apps.a_common.scheme import CommonlyUsedUserSearch
from apps.crud.role import get_role_by_id
from apps.model.permission import PermissionDB
from apps.model.permission2role import Permission2RoleDB
from apps.model.user import UserDB
from apps.model.user2role import User2RoleDB
from apps.model.role import RoleDB
from apps.serializer.user import BaseUserSerializer, CreateUser
from utils.time import timer


def add_user(session: Session, user_data: CreateUser) -> UserDB:
    user = UserDB(
        name=user_data.name,
        sex=user_data.sex,
        phone=user_data.phone,
    )
    user.generate_password_hash(user_data.password)
    session.add(user)
    return user


def get_users_by_id_list(session: Session, user_ids: List[int]) -> List[UserDB]:
    users = session.query(UserDB).filter(UserDB.id.in_(user_ids)).all()
    return users


def get_user_by_id(session: Session, user_id: int) -> UserDB:
    user = session.query(UserDB).filter(UserDB.id == user_id).first()
    return user


def get_user_with_permission_and_group_by_id(session: Session, user_id: int) -> UserDB:
    subquery_group = session.query(RoleDB, User2RoleDB.user_id). \
        filter(User2RoleDB.role_id == RoleDB.id).subquery()
    
    subquery_permission = session.query(PermissionDB.name, Permission2RoleDB.role_id). \
        filter(PermissionDB.id == Permission2RoleDB.permission_id).subquery()
    
    result = session.query(UserDB, subquery_group.c.name, subquery_permission.c.name, subquery_group.c.id). \
        outerjoin(subquery_group, subquery_group.c.user_id == UserDB.id). \
        outerjoin(subquery_permission, subquery_permission.c.role_id == subquery_group.c.id). \
        filter(UserDB.id == user_id) \
        .all()
    
    if len(result) == 0:
        return None
    
    user: UserDB = result[0][0]
    for _, group_name, permission_name, group_id in result:
        if group_name:
            user.role_set.add(group_name)
        if permission_name:
            user.permission_set.add(permission_name)
        if group_id:
            user.role_id_set.add(group_id)
    return user


def get_user_by_phone_number(session: Session, phone_number: str) -> UserDB:
    user = session.query(UserDB).filter(UserDB.phone == phone_number).first()
    return user


def update_user_by_id(session: Session, user_id: int, user_data: BaseUserSerializer) -> UserDB:
    user = session.query(UserDB).filter(UserDB.id == user_id).first()
    user.sex = user_data.sex
    user.phone = user_data.phone
    session.add(user)
    return user


def delete_user_by_id(session: Session, user_id: int) -> UserDB:
    user = session.query(UserDB).filter(UserDB.id == user_id).first()
    session.delete(user)
    return user


@timer
def update_user_identity(session: Session, user_ids: List[int], identity: USER_IDENTITY_LITERAL):
    session.query(UserDB). \
        filter(or_many_condition([UserDB.id == i for i in user_ids])). \
        update({UserDB.user_identity: UserDB.user_identity.op('|')(identity)}, synchronize_session=False)


@timer
def cancel_user_identity(session: Session, user_ids: Set[int], identity: USER_IDENTITY_LITERAL):
    session.query(UserDB). \
        filter(or_many_condition([UserDB.id == i for i in user_ids])). \
        filter(UserDB.user_identity.op('&')(identity) == identity). \
        update({UserDB.user_identity: UserDB.user_identity - identity}, synchronize_session=False)


@timer
def update_and_cancel_user_identity(session: Session, user_ids: List[int], update_identity: USER_IDENTITY_LITERAL, cancel_identity: USER_IDENTITY_LITERAL):
    session.query(UserDB). \
        filter(or_many_condition([UserDB.id == i for i in user_ids])). \
        filter(UserDB.user_identity.op('&')(cancel_identity) == cancel_identity). \
        update({UserDB.user_identity: UserDB.user_identity - cancel_identity + update_identity}, synchronize_session=False)


@timer
def cancel_user_as_admin_if_no_role(session: Session, user_ids: List[int]):
    has_more_group_data = session.query(User2RoleDB.user_id). \
        filter(User2RoleDB.user_id.in_(user_ids)). \
        group_by(User2RoleDB.user_id). \
        having(func.count() > 0)
    
    has_more_group_set = {i[0] for i in has_more_group_data}
    no_more_group_set = set(user_ids) - has_more_group_set
    cancel_user_identity(session, no_more_group_set, UserIdentity.ADMIN)


@timer
def common_user_search(query: Query, params: CommonlyUsedUserSearch) -> Query:
    if params.sex is not None:
        query = query.filter(UserDB.sex == params.sex)
    if params.keyword_name:
        query = query.filter(UserDB.name.ilike(f'%{params.keyword_name}%'))
    if params.user_identity is not None:
        query = query.filter(UserDB.user_identity.op('&')(params.user_identity))
    return query


@timer
def common_user_search_with_permission_check(manager: UserDB, query: Query, session: Session, params: CommonlyUsedUserSearch) -> Tuple[Union[Query, None], Union[AppError, None]]:
    from apps.a_common.permission import has_permission_manage_role
    
    if params.role_id is None:
        return None, InvalidParamError('请选择角色')
    
    if has_permission_manage_role(get_role_by_id(session=session, i=params.role_id), manager):
        query = query.filter(User2RoleDB.role_id == params.role_id)
    else:
        return None, PermissionError('您没有查看这个组的权限')
    
    return common_user_search(query, params), None
