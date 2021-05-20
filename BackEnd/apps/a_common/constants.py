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

NATION_MAP = {
    1: '汉族',
    2: '蒙古族',
    3: '回族',
    4: '藏族',
    5: '维吾尔族',
    6: '苗族',
    7: '彝族',
    8: '壮族',
    9: '布依族',
    10: '朝鲜族',
    11: '满族',
    12: '侗族',
    13: '瑶族',
    14: '白族',
    15: '土家族',
    16: '哈尼族',
    17: '哈萨克族',
    18: '傣族',
    19: '黎族',
    20: '傈僳族',
    21: '佤族',
    22: '畲族',
    23: '高山族',
    24: '拉祜族',
    25: '水族',
    26: '东乡族',
    27: '纳西族',
    28: '景颇族',
    29: '柯尔克孜族',
    30: '土族',
    31: '达斡尔族',
    32: '仫佬族',
    33: '羌族',
    34: '布朗族',
    35: '撒拉族',
    36: '毛难族',
    37: '仡佬族',
    38: '锡伯族',
    39: '阿昌族',
    40: '普米族',
    41: '塔吉克族',
    42: '怒族',
    43: '乌孜别克族',
    44: '俄罗斯族',
    45: '鄂温克族',
    46: '崩龙族',
    47: '保安族',
    48: '裕固族',
    49: '京族',
    50: '塔塔尔族',
    51: '独龙族',
    52: '鄂伦春族',
    53: '赫哲族',
    54: '门巴族',
    55: '珞巴族',
    56: '基诺族',
    57: '其他',
    58: '外国血统中国人士',
}
