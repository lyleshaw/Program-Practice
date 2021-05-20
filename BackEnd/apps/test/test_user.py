from apps.crud.user import get_user_with_permission_and_group_by_id
from apps.model.user import UserDB
from apps.test import assert_response_fail, assert_response_success, clean_all, generate_permission, generate_permission2role, generate_user, generate_user2role, generate_role, get_client, get_session_local
from apps.view.user import user_prefix
from config import API_PREFIX

api_prefix = f"{API_PREFIX}/{user_prefix}"

right_user_data = {
    'sex': 1,
    'name': '小明',
    'phone': "13218655818",
    'password': "123123",
}


def setup_module():
    """ 这个文件下的测试开始之前，会执行这个函数 """


def teardown_module():
    """ 这个文件下的测试结束之后，会执行这个函数 """


def setup_function():
    """ 这个文件下的每个测试运行之前，都会执行这个函数 """
    clean_all()


def teardown_function():
    """ 这个文件下的每个测试运行之后，都会执行这个函数 """


def test_register():
    client = get_client()
    table_data = (
        (right_user_data, True),
        ({
             'sex': 1,
             'phone': "132186818",  # wrong
             'password': "123123",
         }, False),
        ({
             'sex': 100,  # wrong
             'phone': "13218655818",
             'password': "123123",
         }, False),
        ({
             'sex': 0,
             'phone': "13218655818",
             'password': "123123",
         }, False),
    )
    for data, ok in table_data:
        response = client.post(f"{api_prefix}/register", json=data)
        print(response.json())
        assert (response.status_code == 200) == ok
    with get_session_local() as session:
        assert 1 == session.query(UserDB).count()


def test_login():
    client = get_client()
    client.post(f"{api_prefix}/register", json=right_user_data)
    table_data = (
        (right_user_data, True),
        ({
             'password': "123",  # wrong
             'phone': "12321",
         }, False),
        ({
             'password': "123",
             'phone': "1708121"  # wrong
         }, False),
    )
    for data, ok in table_data:
        print(data)
        response = client.post(f"{api_prefix}/login", json=data)
        print(response.json())
        if ok:
            assert response.cookies.get('user-token') != ''
        else:
            assert_response_fail(response)


def test_read_me():
    client = get_client()
    response = client.post(f"{api_prefix}/register", json=right_user_data)
    assert_response_success(response)
    response = client.post(f"{api_prefix}/login", json=right_user_data)
    assert_response_success(response)
    client.cookies['user-token'] = response.cookies.get('user-token')
    response = client.get(f"{api_prefix}/me")
    user_data = assert_response_success(response)
    assert user_data['phone'] == right_user_data['phone']


def test_get_user_with_permission_and_group_by_id():
    with get_session_local() as session:
        # simple
        user = generate_user()
        role = generate_role()
        permission1 = generate_permission()
        permission2 = generate_permission()
        session.add_all((user, role, permission1, permission2))
        session.flush()
        
        session.add_all((
            generate_user2role(user.id, role.id),
            generate_permission2role(permission1.id, role.id),
            generate_permission2role(permission2.id, role.id)
        ))
        session.commit()
        
        user = get_user_with_permission_and_group_by_id(session, user.id)
        assert user is not None
        assert user.permission_set == {permission1.name, permission2.name}
        assert user.role_set == {role.name}
    
    clean_all()
    with get_session_local() as session:
        # more group and permission
        user = generate_user()
        role1 = generate_role()
        role2 = generate_role()
        permission1 = generate_permission()
        permission2 = generate_permission()
        permission3 = generate_permission()
        session.add_all((user, role1, role2, permission1, permission2, permission3))
        session.flush()
        
        session.add_all((
            generate_user2role(user.id, role1.id),
            generate_user2role(user.id, role2.id),
            generate_permission2role(permission1.id, role1.id),
            generate_permission2role(permission2.id, role1.id),
            generate_permission2role(permission3.id, role2.id)
        ))
        session.commit()
        
        user = get_user_with_permission_and_group_by_id(session, user.id)
        assert user is not None
        assert user.permission_set == {permission1.name, permission2.name, permission3.name}
        assert user.role_set == {role1.name, role2.name}
    
    clean_all()
    with get_session_local() as session:
        # has group, no permission
        user = generate_user()
        role1 = generate_role()
        role2 = generate_role()
        session.add_all((user, role1, role2))
        session.flush()
        
        session.add_all((
            generate_user2role(user.id, role1.id),
            generate_user2role(user.id, role2.id),
        ))
        session.commit()
        
        user = get_user_with_permission_and_group_by_id(session, user.id)
        assert user is not None
        assert len(user.permission_set) == 0
        assert user.role_set == {role1.name, role2.name}
    
    clean_all()
    with get_session_local() as session:
        # no group, no permission
        user = generate_user()
        session.add(user)
        session.commit()
        
        user = get_user_with_permission_and_group_by_id(session, user.id)
        assert user is not None
        assert len(user.permission_set) == 0
        assert len(user.role_set) == 0
