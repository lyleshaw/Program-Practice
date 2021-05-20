# coding=utf-8
import traceback
from logging import getLogger

import yagmail
from fastapi.exceptions import RequestValidationError
from requests.exceptions import RequestException
from starlette.background import BackgroundTask

from apps.a_common.error.error_code import ER
from apps.a_common.error.exceptions import AppError, InvalidParamError, NetworkError
from config import DEBUG, SMTP_PWD, SMTP_SERVER, SMTP_USER, TO_MAIL

logger = getLogger(__name__)
NETWORK_ERROR_SET = (RequestException,)


def try_get_my_error(e):
    ex = e
    if isinstance(e, NETWORK_ERROR_SET):
        ex = NetworkError()
    elif isinstance(e, RequestValidationError):
        ex = InvalidParamError()
        if DEBUG:
            ex.fields = e.errors()
    
    return ex


def exception_handler(e):
    from apps.a_common.response import error_response
    e = try_get_my_error(e)
    if not isinstance(e, AppError) or e.code == ER.NOT_DEFINED.code:
        title = '【新错误发生】' + '错误类型' + str(type(e)) + '|请尽快处理。'
        content = "错误概述：\n" + str(e.args) + '\n\n错误栈：\n' + _get_error_stack(e)
        task = BackgroundTask(send_email, title=title, content=content)
        return error_response(code=ER.NOT_DEFINED.code, detail="服务错误,请联系我们", task=task)
    
    return error_response(error=e, fields=e.fields)


def send_email(title: str, content: str):
    if not TO_MAIL:
        return
    
    yag = yagmail.SMTP(user=SMTP_USER, password=SMTP_PWD, host=SMTP_SERVER)
    yag.send(TO_MAIL, title, content)


def _get_error_stack(exc) -> str:
    content = "".join(
        traceback.format_exception(
            etype=type(exc), value=exc, tb=exc.__traceback__
        )
    )
    return content
