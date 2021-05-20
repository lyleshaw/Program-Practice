from apps.a_common.constants import MANAGE_ROLE_PERMISSION_NAME
from apps.test import assert_response_fail, assert_response_success, clean_all, generate_role, generate_user2role, generate_user, get_client, get_session_local, override_get_user
from apps.view.manage_user import manage_user_prefix
from config import API_PREFIX

api_prefix = f"{API_PREFIX}/{manage_user_prefix}"


def setup_module():
    """ 这个文件下的测试开始之前，会执行这个函数 """


def teardown_module():
    """ 这个文件下的测试结束之后，会执行这个函数 """


def setup_function():
    """ 这个文件下的每个测试运行之前，都会执行这个函数 """
    clean_all()


def teardown_function():
    """ 这个文件下的每个测试运行之后，都会执行这个函数 """


def test_search_user_search():
    with get_session_local() as session:
        role = generate_role()
        session.add(role)
        user_line = [generate_user() for _ in range(10)]
        for i, user in enumerate(user_line):
            user.name = str(i)
            user.sex = i % 2 + 1
        user2role_line = []
        session.add_all(user_line)
        session.flush()
        for user in user_line:
            user2role_line.append(generate_user2role(user_id=user.id, role_id=role.id))
        session.add_all(user2role_line)
        session.commit()
    
    client = get_client()
    with override_get_user():
        response = client.get(f'{api_prefix}/', params={'role_id': role.id})
        assert_response_fail(response)
    
    with override_get_user() as user:
        user.role_set.add(MANAGE_ROLE_PERMISSION_NAME.format(role_id=role.id))
        user.role_id_set.add(role.id)
        response = client.get(f'{api_prefix}/', params={'role_id': role.id})
        data = assert_response_success(response)
        assert len(data) == 10
        response = client.get(f'{api_prefix}/', params={'role_id': role.id, 'sex': 1})
        data = assert_response_success(response)
        assert len(data) == 5


def test_read_op_user_():
    with override_get_user(is_superuser=True) as user:
        client = get_client()
        response = client.get(f'{api_prefix}/{user.id}')
        assert_response_success(response)


def test_update_op_user_():
    with override_get_user(is_superuser=True) as user:
        client = get_client()
        response = client.put(f'{api_prefix}/{user.id}', json={'sex': 1, 'phone': '13218655818', 'name': '小明', 'address': '123'})
        assert_response_success(response)


def test_manage_reset_password():
    with override_get_user(is_superuser=True) as user:
        client = get_client()
        response = client.post(f'{api_prefix}/reset-password', json=[user.id])
        data = assert_response_success(response)
        assert data == {'count': 1}
        
        response = client.post('/v1/api/users/login', json=dict(phone=user.phone, password='123456789'))
        assert_response_success(response)


def test_manager_create_user():
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.post(f'{api_prefix}', json={'sex': 1, 'phone': '13218655818', 'name': '小明'})
        assert_response_success(response)
    
    response = client.post('/v1/api/users/login', json=dict(phone='13218655818', password=''))
    assert_response_success(response)
