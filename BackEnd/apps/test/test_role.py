from apps.a_common.constants import UserIdentity
from apps.a_common.scheme import PageInfo
from apps.crud.role import get_users_by_role_id
from apps.model.user import UserDB
from apps.model.user2role import User2RoleDB
from apps.model.role import RoleDB
from apps.test import assert_response_fail, assert_response_success, clean_all, generate_user, generate_user2role, generate_role, get_client, get_session_local, override_get_user
from apps.view.role import role_prefix
from config import API_PREFIX
from utils.encode import uuid

api_prefix = f"{API_PREFIX}/{role_prefix}"


def setup_module():
    """ 这个文件下的测试开始之前，会执行这个函数 """


def teardown_module():
    """ 这个文件下的测试结束之后，会执行这个函数 """


def setup_function():
    """ 这个文件下的每个测试运行之前，都会执行这个函数 """
    clean_all()


def teardown_function():
    """ 这个文件下的每个测试运行之后，都会执行这个函数 """


def test_get_users_by_role_id_query():
    with get_session_local() as session:
        user1 = generate_user()
        user2 = generate_user()
        user3 = generate_user()
        role1 = generate_role()
        session.add_all((user1, user2, user3, role1))
        session.flush()
        session.add(User2RoleDB(user_id=user1.id, role_id=role1.id))
        session.add(User2RoleDB(user_id=user2.id, role_id=role1.id))
        session.commit()
        
        paginate = get_users_by_role_id(session, role1.id, PageInfo(page_id=1, page_size=10))
        assert len(paginate.items) == 2
        for user in paginate.items:
            assert user.id != user3.id


def test_role_list_by_superuser():
    with get_session_local() as session:
        for i in range(20):
            session.add(generate_role())
        session.commit()
    
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.get(api_prefix)
        print(api_prefix)
        assert_response_success(response)
        assert len(response.json()['data']) == 20
        
        response = client.get(api_prefix, params=dict(page_size=10))
        assert_response_success(response)
        assert len(response.json()['data']) == 10
        
        response = client.get(api_prefix, params=dict(page_id=2, page_size=10))
        assert_response_success(response)
        assert len(response.json()['data']) == 10


def test_role_list_by_user_group():
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.post(api_prefix, json=dict(name=uuid()))
        g1 = assert_response_success(response)
        
        response = client.post(api_prefix, json=dict(name=uuid()))
        g2 = assert_response_success(response)
        
        response = client.post(api_prefix, json=dict(name=uuid(), parent_id=g1['id']))
        g3 = assert_response_success(response)
        
        response = client.post(api_prefix, json=dict(name=uuid(), parent_id=g3['id']))
        g4 = assert_response_success(response)
    
    with override_get_user() as user:
        user.role_id_set.add(g2['id'])
        user.role_set.add(g2['name'])
        
        client = get_client()
        response = client.get(api_prefix)
        data = assert_response_success(response)
        assert len(data) == 1
    
    with override_get_user() as user:
        user.role_id_set.add(g3['id'])
        user.role_set.add(g3['name'])
        
        client = get_client()
        response = client.get(api_prefix)
        data = assert_response_success(response)
        assert len(data) == 2
    
    with override_get_user() as user:
        user.role_id_set.add(g1['id'])
        user.role_set.add(g1['name'])
        
        client = get_client()
        response = client.get(api_prefix)
        data = assert_response_success(response)
        assert len(data) == 3


def test_add_role():
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.post(api_prefix, json=dict(name=uuid()))
        g1 = assert_response_success(response)
        assert g1['grand_id'] == ''
        assert g1['parent_id'] == 0
        
        response = client.post(api_prefix, json=dict(name=uuid()))
        g2 = assert_response_success(response)
        
        response = client.post(api_prefix, json=dict(name=uuid(), parent_id=g1['id']))
        g3 = assert_response_success(response)
        assert g3['grand_id'] == f'|{g1["id"]}|'
        assert g3['parent_id'] == g1['id']
        
        response = client.post(api_prefix, json=dict(name=uuid(), parent_id=g3['id']))
        g4 = assert_response_success(response)
        assert g4['grand_id'] == f'|{g1["id"]}|{g3["id"]}|'
        assert g4['parent_id'] == g3['id']
    
    with get_session_local() as session:
        assert session.query(RoleDB).count() == 4


def test_role_user_list():
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.post(api_prefix, json=dict(name=uuid()))
        g1 = assert_response_success(response)
        
        response = client.post(api_prefix, json=dict(name=uuid(), parent_id=g1['id']))
        g2 = assert_response_success(response)
    
    with get_session_local() as session:
        user11 = generate_user()
        user12 = generate_user()
        user2 = generate_user()
        user3 = generate_user()
        session.add_all((user11, user12, user2, user3))
        session.flush()
        session.add_all((generate_user2role(user11.id, g1['id']),
                         generate_user2role(user12.id, g1['id']),
                         generate_user2role(user2.id, g2['id']),
                         generate_user2role(user2.id, g2['id'])
                         ))
        session.commit()
        
        with override_get_user() as user:
            user.role_id_set.add(g1['id'])
            user.role_set.add(g1['name'])
            client = get_client()
            response = client.get(f'{api_prefix}/{g1["id"]}/users')
            data = assert_response_success(response)
            assert len(data) == 2
            
            response = client.get(f'{api_prefix}/{g2["id"]}/users')
            data = assert_response_success(response)
            print(data)
            assert len(data) == 1
            assert data[0]['id'] == user2.id


def test_update_role_():
    with get_session_local() as session:
        role1 = generate_role()
        role2 = generate_role()
        session.add_all((role1, role2))
        session.commit()
        
        with override_get_user(is_superuser=True):
            client = get_client()
            response = client.put(f'{api_prefix}/{role1.id}', json=dict(name='123'))
            data = assert_response_success(response)
            assert data['name'] == '123'
            session.refresh(role1)
            assert role1.name == '123'
            
            response = client.put(f'{api_prefix}/{role2.id}', json=dict(name='123'))
            assert_response_fail(response)


def test_del_role():
    with get_session_local() as session:
        user11 = generate_user()
        user12 = generate_user()
        user2 = generate_user()
        user3 = generate_user()
        role1 = generate_role()
        role2 = generate_role()
        session.add_all((user11, user12, user2, user3, role1, role2))
        session.flush()
        session.add_all((generate_user2role(user11.id, role1.id),
                         generate_user2role(user12.id, role1.id),
                         generate_user2role(user2.id, role2.id)
                         ))
        session.commit()
        
        with override_get_user(is_superuser=True):
            client = get_client()
            response = client.delete(f'{api_prefix}/{role1.id}')
            assert_response_success(response)
            r: User2RoleDB = session.query(User2RoleDB).one()
            assert r.user_id == user2.id
            assert r.role_id == role2.id


def test_add_user_to_role_by_superuser():
    with get_session_local() as session:
        user1 = generate_user()
        user2 = generate_user()
        user3 = generate_user()
        role1 = generate_role()
        role2 = generate_role()
        session.add_all((user1, user2, user3, role1, role2))
        session.commit()
    
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.post(f'{api_prefix}/{role1.id}/users:add', json=[user1.id, user2.id])
        assert_response_success(response)
        response = client.get(f'{api_prefix}/{role1.id}/users')
        data = assert_response_success(response)
        assert len(data) == 2
        
        response = client.post(f'{api_prefix}/{role1.id}/users:add', json=[user2.id, user3.id])
        assert_response_success(response)
        response = client.get(f'{api_prefix}/{role1.id}/users')
        data = assert_response_success(response)
        assert len(data) == 3


def test_del_user_to_role():
    with get_session_local() as session:
        user1 = generate_user()
        user2 = generate_user()
        user3 = generate_user()
        role1 = generate_role()
        role2 = generate_role()
        session.add_all((user1, user2, user3, role1, role2))
        session.flush()
        session.add_all((generate_user2role(user1.id, role1.id),
                         generate_user2role(user1.id, role1.id),
                         generate_user2role(user2.id, role1.id),
                         generate_user2role(user2.id, role2.id),
                         generate_user2role(user3.id, role2.id)
                         ))
        session.commit()
        
        with override_get_user(is_superuser=True):
            client = get_client()
            response = client.post(f'{api_prefix}/{role1.id}/users:delete', json=[user1.id])
            assert_response_success(response)
            response = client.get(f'{api_prefix}/{role1.id}/users')
            data = assert_response_success(response)
            assert len(data) == 1
            
            response = client.post(f'{api_prefix}/{role1.id}/users:delete', json=[user2.id, user3.id])
            assert_response_success(response)
            response = client.get(f'{api_prefix}/{role1.id}/users')
            data = assert_response_success(response)
            assert len(data) == 0
            response = client.get(f'{api_prefix}/{role2.id}/users')
            data = assert_response_success(response)
            assert len(data) == 2


def test_update_delete_not_find():
    not_exist_id = -1
    
    with override_get_user(is_superuser=True):
        client = get_client()
        response = client.post(f'{api_prefix}/{not_exist_id}/users:delete', json=[1, 2])
        assert_response_fail(response)
        assert response.json()['code'] == 404
        
        response = client.post(f'{api_prefix}/{not_exist_id}/users:add', json=[1, 2])
        assert_response_fail(response)
        assert response.json()['code'] == 404
        
        response = client.delete(f'{api_prefix}/{not_exist_id}')
        assert_response_fail(response)
        assert response.json()['code'] == 404
        
        response = client.put(f'{api_prefix}/{not_exist_id}', json=dict(name=uuid()))
        assert_response_fail(response)
        assert response.json()['code'] == 404


def test_update_user_as_secretary_and_cancel_user_as_secretary_if_no_user_group():
    with get_session_local() as session:
        u1 = generate_user()
        u2 = generate_user()
        u3 = generate_user()
        u1.user_identity = UserIdentity.ADMIN
        u3.user_identity = UserIdentity.ADMIN
        g1 = generate_role()
        g2 = generate_role()
        session.add_all((u1, u2, u3, g1, g2))
        session.commit()
    
    def assert_user_identity(u1_id, u2_id, u3_id, i1, i2, i3):
        with get_session_local() as session:
            u1 = session.query(UserDB).get(u1_id)
            u2 = session.query(UserDB).get(u2_id)
            u3 = session.query(UserDB).get(u3_id)
            
            assert u1.user_identity == i1
            assert u2.user_identity == i2
            assert u3.user_identity == i3
    
    client = get_client()
    with override_get_user(is_superuser=True):
        # test add
        response = client.post(f'{api_prefix}/{g1.id}/users:add', json=[u1.id, u2.id, u3.id])
        assert_response_success(response)
        assert_user_identity(u1.id, u2.id, u3.id, UserIdentity.COMMON_USER + UserIdentity.ADMIN, UserIdentity.COMMON_USER + UserIdentity.ADMIN, UserIdentity.COMMON_USER + UserIdentity.ADMIN)
        
        # test add more
        response = client.post(f'{api_prefix}/{g2.id}/users:add', json=[u2.id, u3.id])
        assert_response_success(response)
        assert_user_identity(u1.id, u2.id, u3.id, UserIdentity.COMMON_USER + UserIdentity.ADMIN, UserIdentity.COMMON_USER + UserIdentity.ADMIN, UserIdentity.COMMON_USER + UserIdentity.ADMIN)
        
        # test delete
        response = client.post(f'{api_prefix}/{g1.id}/users:delete', json=[u1.id, u2.id])
        assert_response_success(response)
        assert_user_identity(u1.id, u2.id, u3.id, UserIdentity.COMMON_USER, UserIdentity.ADMIN, UserIdentity.ADMIN)
        
        # test delete more
        response = client.post(f'{api_prefix}/{g2.id}/users:delete', json=[u2.id, u3.id])
        assert_response_success(response)
        assert_user_identity(u1.id, u2.id, u3.id, UserIdentity.COMMON_USER, UserIdentity.COMMON_USER, UserIdentity.ADMIN)
        
        # test delete all
        response = client.post(f'{api_prefix}/{g1.id}/users:delete', json=[u2.id, u3.id])
        assert_response_success(response)
        assert_user_identity(u1.id, u2.id, u3.id, UserIdentity.COMMON_USER, UserIdentity.COMMON_USER, UserIdentity.COMMON_USER)
