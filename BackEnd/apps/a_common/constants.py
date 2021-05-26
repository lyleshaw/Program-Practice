from typing import Tuple

from typing_extensions import Literal

""" 这里放一些不会改变的东西 比如类型到数字的映射关系 """

MANAGE_ROLE_PERMISSION_NAME = 'manage-user:{role_id}'


def to_choice(cls: object) -> Tuple:
    return_choice = ()
    for key, value in cls.__dict__.items():
        if not callable(getattr(cls, key)) and not key.startswith("__"):
            return_choice = return_choice + ((value, key),)
    return return_choice


def to_map(cls: object) -> dict:
    return_dict = {}
    for key, value in cls.__dict__.items():
        if not callable(getattr(cls, key)) and not key.startswith("__"):
            return_dict[value] = key
    return return_dict


class Sex:
    MALE = 1
    FEMALE = 2


SEX_LITERAL = Literal[1, 2]
SEX_CHOICE = to_choice(Sex)
SEX_MAP = to_map(Sex)


class HealthCodeStatus:
    GREEN = 1
    YELLOW = 2
    ORANGE = 3
    RED = 4
    UNSIGNED = 5


HealthCode_Literal = Literal[1, 2, 3, 4, 5]
HealthCode_Choice = to_choice(HealthCodeStatus)
HealthCode_Map = to_map(HealthCodeStatus)


class PermissionType:
    COMMON = 1
    COLLEGE_MANAGE = 2


PERMISSION_TYPE_LITERAL = Literal[1, 2]
PERMISSION_TYPE_CHOICE = to_choice(PermissionType)
PERMISSION_TYPE_MAP = to_map(PermissionType)


class UserIdentity:
    COMMON_USER = 0  # 普通用户
    ADMIN = 2 ** 0  # 管理员


USER_IDENTITY_LITERAL = Literal[0, 1]
USER_IDENTITY_CHOICE = to_choice(UserIdentity)
USER_IDENTITY_MAP = to_map(UserIdentity)
