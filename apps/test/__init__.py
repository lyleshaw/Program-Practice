import random
from contextlib import contextmanager

from fastapi.testclient import TestClient
from requests import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import MetaData

from apps import app
from apps.a_common.db import Base, get_session
from apps.logic.user import get_user, get_user_id
from apps.model.permission import PermissionDB
from apps.model.permission2role import Permission2RoleDB
from apps.model.user import UserDB
from apps.model.user2role import User2RoleDB
from apps.model.role import RoleDB
from install.test.config import SQL_CONNECT_ARGS, SQL_URL
from utils.encode import uuid

"""
测试文件以test_开头
测试函数以test_开头
断言全都使用assert
"""

""" 一般来说，有些模块测试运行之前，需要一些数据。比如测试Permission的时候，我们假定User和Group都是没问题的。所以直接用写数据库（而非API）的方式来添加一些数据
    因此之后的测试，文件的最上面，会写上

    def setup_module():
        add_some_user()
        add_some_permission()
        ...

    def teardown_module():
        clean_all()
"""

"""
表驱动测试，就是把 测试的数据 和 预期的结果，都写在一行，然后for循环多行，去运行和验证，例如：
test_table = (
    (3, 4, 7),
    (5, 5, 10),
    (1, 10, 11)
)
for a, b, r in test_able:
    assert add(a, b) == r
"""

engine = create_engine(SQL_URL, connect_args=SQL_CONNECT_ARGS)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
metadata: MetaData = Base.metadata
metadata.drop_all(bind=engine)
metadata.create_all(bind=engine)


def override_get_session():
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = override_get_session


@contextmanager
def get_session_local() -> Session:
    """
    获得一个session，并且会自动关闭
    example:
        with get_session_local() as session:
            do_somethings()
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def override_get_user(user=None, is_superuser=False):
    """
    覆盖了对User的依赖，通过直接给定User，可以测试一些需要权限的接口
    目前只做到，提供一个普通的User
    example:
        with override_get_user():
            do_somethings()
    """
    if user is None:
        with get_session_local() as session:
            user = generate_user()
            user.is_superuser = is_superuser
            session.add(user)
            session.commit()
    print(user)
    try:
        app.dependency_overrides[get_user] = lambda: user
        app.dependency_overrides[get_user_id] = lambda: user.id
        yield user
    finally:
        del app.dependency_overrides[get_user]
        del app.dependency_overrides[get_user_id]


def get_client() -> TestClient:
    return TestClient(app)


def setup_module():
    """ 这个文件下的测试开始之前，会执行这个函数 """


def teardown_module():
    """ 这个文件下的测试结束之后，会执行这个函数 """


def setup_function():
    """ 这个文件下的每个测试运行之前，都会执行这个函数 """


def teardown_function():
    """ 这个文件下的每个测试运行之后，都会执行这个函数 """


def assert_response_fail(response: Response):
    """ 判断一个response是否失败 """
    if response.status_code != 200:
        return
    
    data = response.json()
    if data['code'] == 200:
        assert data['code'] == -1


def assert_response_success(response: Response):
    """ 判断一个response是否成功，返回数据 """
    print(response.status_code, response.content)
    assert response.status_code == 200
    data = response.json()
    assert data['code'] == 200
    return data['data']


def clean_all():
    """ 清空所有数据 """
    with get_session_local() as session:
        for table in reversed(metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()


def generate_user() -> UserDB:
    phone = random.randint(17366637010, 17366737010)
    return UserDB(name='lyle', password='123', sex=1, phone=str(phone))


def generate_manager() -> UserDB:
    phone = random.randint(17366637010, 17366737010)
    manager = UserDB(name='admin', password='123', sex=1, phone=str(phone))
    manager.permission_set = {"manage-organization:1"}
    return manager


def generate_manager_with_org(org_id: int) -> UserDB:
    phone = random.randint(17366637010, 17366737010)
    manager = UserDB(name='admin', password='123', sex=1, phone=str(phone))
    manager.permission_set = {f"manage-organization:{org_id}"}
    return manager


def generate_role() -> RoleDB:
    return RoleDB(name=uuid())


def generate_user2role(user_id: int, role_id: int) -> User2RoleDB:
    return User2RoleDB(user_id=user_id, role_id=role_id)


def generate_permission(name=None):
    return PermissionDB(name=name or uuid())


def generate_permission2role(permission_id: int, role_id: int) -> Permission2RoleDB:
    return Permission2RoleDB(permission_id=permission_id, role_id=role_id)
