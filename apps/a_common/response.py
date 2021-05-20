# coding=utf-8
from logging import getLogger
from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.background import BackgroundTask

from apps.a_common.db import Pagination
from config import ADDRESS
from utils.encode import json

logger = getLogger(__name__)
"""
{
    'code': 100010,             # error code
    'detail': detail,           # show for user
    'fields': fields,           # show for dev, list
    'success': true             # suc or fail
    'data': data,               # data if success else null, be list or dict
}
"""


def success_response(data: (list, dict) = None, page: dict = None) -> JSONResponse:
    result = {
        'code': 200,  # error code
        'detail': None,  # show for user
        'fields': None,  # show for dev, list
        'success': True,  # suc or fail
        'data': data,  # data if success else null, be list or dict
    }
    if page:
        result.update(page)
    logger.info(f'{result}')
    return Response(json.encode(result), media_type="application/json")


def error_response(error=None, code=None, detail=None, fields: list = None, task: BackgroundTask = None):
    """
    给StandardErrorRecord， 或者同时给code和detail
    """
    from apps.a_common.error import ER
    if code is None and detail is None:
        error = ER.NOT_DEFINED if error is None else error
        code, detail = error.code, error.detail
    
    if not fields and error:
        fields = error.fields
    result = {
        'code': code,
        'detail': detail,
        'fields': fields,
        'success': False,
        'data': None,
    }
    return JSONResponse(result, background=task)


def url_for(endpoint, **kwargs):
    if kwargs:
        return f"{ADDRESS}{endpoint}?{urlencode(kwargs)}"
    return f"{ADDRESS}{endpoint}"


def make_paginate_info(paginate: Pagination, request: Request):
    """ 制作传统分页的分页信息 """
    url = request.url._url
    
    if url.startswith("http"):
        url_params = url.split("?")[0]
        temp_url_list = url_params.split("/")[3:]
        endpoint = '/' + '/'.join(temp_url_list)
        params = request.query_params.__dict__['_dict']
        
        params['page_size'] = paginate.page_size
        
        params['page_id'] = paginate.next_page_id
        next = None if params['page_id'] is None else url_for(endpoint, **params)
        params['page_id'] = paginate.prev_page_id
        previous = None if params['page_id'] is None else url_for(endpoint, **params)
    else:
        raise Exception()
    
    return dict(next=next, previous=previous, count=paginate.total)


def empty_paginate_response():
    return success_response([], dict(next=None, previous=None, count=0))
