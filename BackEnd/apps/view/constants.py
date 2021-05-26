from fastapi import APIRouter

from apps.a_common.constants import PERMISSION_TYPE_MAP, SEX_MAP, HealthCode_Map
from apps.a_common.response import success_response

constants_router = APIRouter()
constants_prefix = 'constants'


@constants_router.get("", summary="用于查询所有的constants")
async def get_constants():
    data = {
        'sex': SEX_MAP,
        'permission_type': PERMISSION_TYPE_MAP,
        'health_code': HealthCode_Map
    }
    return success_response(data)
