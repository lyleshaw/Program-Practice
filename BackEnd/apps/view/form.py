from logging import getLogger

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from apps.a_common.db import get_session, Pagination
from apps.a_common.response import make_paginate_info, success_response
from apps.a_common.scheme import PageInfo, PageInfo_

from apps.crud.form import add_form, get_form_by_search, delete_form_by_id
from apps.logic.user import get_user
from apps.model.user import UserDB
from apps.model.form import FormDB
from apps.serializer.form import FormSerializer, FormSearchSerializer, to_FormDetailSerializer, to_UserDetailSerializerList

form_router = APIRouter()
form_prefix = 'form'
logger = getLogger(__name__)


@form_router.post("", summary="创建表单")
async def create_form(form_data: FormSerializer, session: Session = Depends(get_session)):
    form = add_form(session=session, form_data=form_data)
    session.commit()
    return success_response(to_FormDetailSerializer(form))


@form_router.get("", summary="管理员查看全部表单")
async def get_all_form(request: Request, page_info: PageInfo = Depends(PageInfo_), manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    query = session.query(FormDB)
    paginate = Pagination(query, page_info=page_info)
    paginate_info = make_paginate_info(paginate, request)
    data = [to_FormDetailSerializer(form) for form in paginate.items]
    return success_response(data, paginate_info)


@form_router.post("/search", summary="管理员搜索表单")
async def get_all_form(request: Request, search_condiction: FormSearchSerializer, page_info: PageInfo = Depends(PageInfo_), manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    query = get_form_by_search(session=session, search_condiction=search_condiction)
    paginate = Pagination(query, page_info=page_info)
    paginate_info = make_paginate_info(paginate, request)
    data = [to_FormDetailSerializer(form) for form in paginate.items]
    return success_response(data, paginate_info)


@form_router.delete("/{form_id}", summary="管理员删除指定表单")
async def get_all_form(request: Request, form_id: int, manager: UserDB = Depends(get_user), session: Session = Depends(get_session)):
    form = delete_form_by_id(session=session, form_id=form_id)
    return success_response(form)
