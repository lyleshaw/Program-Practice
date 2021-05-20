# coding=utf-8
import time
from logging import getLogger

from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware, ALL_METHODS, SAFELISTED_HEADERS

from apps.a_common.db import Base
from apps.a_common.error import AppError, ER, exception_handler, exceptions, PermissionError
from apps.foundation import engine
from apps.logconfig import init_logger_config
from apps.view.constants import constants_prefix, constants_router, constants_router
from apps.view.file import file_prefix, file_router, file_router
from apps.view.manage_user import manage_user_prefix, manage_user_router
from apps.view.permission import permission_prefix, permission_router
from apps.view.user import user_prefix, user_router, user_router
from apps.view.role import role_prefix, role_router, role_router
from config import API_PREFIX, DEBUG, DEFAULT_APP_NAME

# 命名规则如下，蓝图加上后缀，避免发生命名冲突，所有的资源都以复数形式呈现

logger = getLogger(__name__)
ROUTERS = [
    (user_router, [user_prefix], user_prefix),
    (file_router, [file_prefix], file_prefix),
    (constants_router, [constants_prefix], constants_prefix),
    (role_router, [role_prefix], role_prefix),
    (permission_router, [permission_prefix], permission_prefix),
    (manage_user_router, [manage_user_prefix], manage_user_prefix),
]


def create_app(name=DEFAULT_APP_NAME, **settings_override):
    app = FastAPI(title=name)
    config_app(app)
    add_middleware(app)
    init_foundations(app)
    include_router(app)
    return app


def config_app(app: FastAPI):
    if not DEBUG:
        app.docs_url = None
        app.redoc_url = None


def include_router(app: FastAPI):
    for router, tags, prefix in ROUTERS:
        app.include_router(router, tags=tags, prefix=f'{API_PREFIX}/{prefix}')


def add_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=ALL_METHODS,
        allow_headers={"Accept", "Accept-Language", "Content-Language", "Content-Type", 'Authorization'},
    )
    
    # @app.middleware('http')
    # async def add_cors_middle(request: Request, call_next):
    #     response: Response = await call_next(request)
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     response.headers['Access-Control-Allow-Methods'] = '*'
    #     response.headers['Access-Control-Allow-Headers'] = '*'
    #     response.headers['Access-Control-Allow-Credentials'] = 'true'
    #     return response
    
    @app.middleware("http")
    async def request_timer_mark(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f'{request.url} cost: {process_time}')
        return response
    
    @app.exception_handler(AppError)
    def error_handler(request: Request, e: AppError):
        return exception_handler(e)
    
    @app.exception_handler(Exception)
    def error_handler(request: Request, e: AppError):
        return exception_handler(e)


def init_foundations(app: FastAPI):
    init_logger_config()
    pass


app = create_app()
