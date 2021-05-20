import functools
from logging import getLogger
from sqlalchemy.orm import Session
from typing import List, Tuple

from apps.a_common.db import or_many_condition
from apps.a_common.constants import MANAGE_ROLE_PERMISSION_NAME
from apps.a_common.error import PermissionError
from apps.model.user import UserDB
from apps.model.role import RoleDB

logger = getLogger(__name__)

constants_permission_set = {
    MANAGE_ROLE_PERMISSION_NAME
}


def has_permission_decorator(permission_name: str):
    constants_permission_set.add(permission_name)
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user = _find_user(*args, **kwargs)
            if not has_permission(user, permission_name):
                raise PermissionError()
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def has_permission(user: UserDB, name: str) -> bool:
    if user is None:
        return False
    
    if name not in user.permission_set and not user.is_superuser:
        return False
    
    return True


def _find_user(*args, **kwargs):
    if "user" in kwargs:
        return kwargs['user']
    if 'manager' in kwargs:
        return kwargs['manager']
    
    for a in args:
        if isinstance(a, UserDB):
            return a
    
    return


def is_superuser(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        user = _find_user(*args, **kwargs)
        if user is None or not user.is_superuser:
            raise PermissionError()
        
        return await func(*args, **kwargs)
    
    return wrapper


def has_permission_manage_role(role: RoleDB, user: UserDB) -> bool:
    """ 查询是否有对role操作的权限，这里比较特殊，是通过role来判断role """
    if role is None or user is None:
        return False
    
    if user.is_superuser:
        return True
    
    #  用户有group的父辈group的管理权限，或者直接管理这个group
    if len(role.grand_id_set & user.role_id_set) > 0 or role.id in user.role_id_set:
        return True
    
    return False


def has_permission_manage_user(client: UserDB, user: UserDB) -> bool:
    """ 查询是否有对单个用户操作的权限 """
    if client.is_superuser:
        return True
    
    if MANAGE_ROLE_PERMISSION_NAME.format(role_id=user.role_id_set) in client.permission_set:
        return True
    
    logger.warning(f'{client} try to manage user: {user}')
    return False


def get_user_role_id(session: Session, id_list: List[int]) -> List[Tuple[int, int]]:
    users = session.query(UserDB).filter(or_many_condition([UserDB.id == i for i in id_list])).all()
    role_ids = []
    for user in users:
        role_ids.append((user.id, user.role_id_set))
    return role_ids


def has_permission_manage_user_ids(session: Session, client: UserDB, user_ids: List[int]) -> Tuple[bool, List[int]]:
    """ 查询是否有对一群用户操作的权限 """
    user_data_list = get_user_role_id(session, user_ids)
    
    if client.is_superuser:
        return True, [i[0] for i in user_data_list]
    
    for user_id, role_id in user_data_list:
        if MANAGE_ROLE_PERMISSION_NAME.format(role_id=role_id) in client.permission_set:
            continue
        logger.warning(f'{client} try to manage user: {user_id}')
        return False, []
    
    return True, [i[0] for i in user_data_list]
