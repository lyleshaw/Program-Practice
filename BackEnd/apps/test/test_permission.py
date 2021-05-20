from fastapi.testclient import TestClient

from apps.a_common.permission import constants_permission_set
from apps.model.permission import PermissionDB
from apps.test import app, assert_response_success, clean_all, generate_permission, get_client, get_session_local, override_get_user
from apps.view.permission import permission_prefix
from config import API_PREFIX
from utils.encode import uuid

api_prefix = f"{API_PREFIX}/{permission_prefix}"


def setup_module():
    """ 这个文件下的测试开始之前，会执行这个函数 """


def teardown_module():
    """ 这个文件下的测试结束之后，会执行这个函数 """


def setup_function():
    """ 这个文件下的每个测试运行之前，都会执行这个函数 """
    clean_all()


def teardown_function():
    """ 这个文件下的每个测试运行之后，都会执行这个函数 """


def test_permission_list():
    with get_session_local() as session:
        session.add_all(tuple(generate_permission() for i in range(20)))
        session.commit()
    
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.get(api_prefix, params=dict(page_id=1, page_size=10))
        data = assert_response_success(response)
        assert len(data) == 10
        
        response = client.get(api_prefix, params=dict(page_id=2, page_size=10))
        data = assert_response_success(response)
        assert len(data) == 10
        
        response = client.get(api_prefix, params=dict(page_id=2, page_size=15))
        data = assert_response_success(response)
        assert len(data) == 5


def test_add_permission():
    old = 0
    with get_session_local() as session:
        old = session.query(PermissionDB).count()
    
    with override_get_user(is_superuser=True):
        client = get_client()
        for i in range(3):
            response = client.post(api_prefix, json=dict(name=uuid()))
            assert_response_success(response)
    
    with get_session_local() as session:
        assert session.query(PermissionDB).count() == old + 3


def test_update_permission():
    with get_session_local() as session:
        permission = generate_permission()
        session.add(permission)
        session.commit()
        
        new_name = uuid()
        with override_get_user(is_superuser=True):
            client = get_client()
            response = client.put(f'{api_prefix}/{permission.id}', json=dict(name=new_name))
            assert_response_success(response)
        
        session.refresh(permission)
        assert permission.name == new_name


def test_delete_permission():
    with get_session_local() as session:
        permission = generate_permission()
        session.add(permission)
        session.flush()
        old = session.query(PermissionDB).count()
        session.commit()
        
        with override_get_user(is_superuser=True):
            client = get_client()
            print(f'{api_prefix}/{permission.id}')
            response = client.delete(f'{api_prefix}/{permission.id}')
            assert_response_success(response)
        
        assert session.query(PermissionDB).count() == old - 1


def test_permission_collect():
    with TestClient(app):
        assert len(constants_permission_set) != 0
