import abc
from typing import List

from fastapi import Query
from pydantic import BaseModel, Field

from apps.a_common.constants import Sex

"""
放一些通用的验证字段，比如手机号，邮编，身份证
"""
PhoneField = Field(..., regex=r"^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9]|9[0-9])\d{8}$", description="手机号码，带有正则验证", title="手机号码")
IDCardField = Field(..., regex=r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$', description="身份证号，带有正则验证", title="身份证号")


class ParamsBase:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


class PageInfo(ParamsBase):
    page_id: int
    page_size: int


def PageInfo_(page_id: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50)) -> PageInfo:
    return PageInfo(page_id=page_id, page_size=page_size)


class _CommonlyUsedUserSearch(BaseModel, abc.ABC):
    sex: int = None
    keyword_name: str = ''
    user_identity: int = None
    role_id: int = None


class CommonlyUsedUserSearch(_CommonlyUsedUserSearch, ParamsBase):
    pass


def CommonlyUsedUserSearch_(sex: int = Query(None, ge=Sex.MALE, le=Sex.FEMALE),
                            keyword_name: str = '',
                            user_identity: int = None,
                            role_id: int = None) -> CommonlyUsedUserSearch:
    return CommonlyUsedUserSearch(sex=sex, keyword_name=keyword_name, user_identity=user_identity, role_id=role_id)


class UserSubSearch(_CommonlyUsedUserSearch):
    user_id_list: List[int] = []
    exclude_user_id_list: List[int] = []
