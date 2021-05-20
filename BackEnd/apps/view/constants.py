from fastapi import APIRouter

from apps.a_common.constants import NATION_MAP, PERMISSION_TYPE_MAP, SEX_MAP, USER_IDENTITY_MAP
from apps.a_common.response import success_response

constants_router = APIRouter()
constants_prefix = 'constants'


@constants_router.get("", summary="用于查询所有的constants")
async def get_constants():
    data = {
        'user_identity': USER_IDENTITY_MAP,
        'sex': SEX_MAP,
        'permission_type': PERMISSION_TYPE_MAP,
        'nation': NATION_MAP,
    }
    return success_response(data)
