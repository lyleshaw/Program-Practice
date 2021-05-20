from apps.a_common.constants import SEX_CHOICE, SEX_MAP
from apps.a_common.db import Pagination
from apps.a_common.jwt import decode_token, encode_token
from apps.a_common.storage import get_filename_without_uuid_prefix, temp_file_name
from apps.model.role import RoleDB
from apps.test import clean_all, generate_role, get_client, get_session_local
from utils.encode import generate_password_hash, is_right_password


def setup_function():
    """ 这个文件下的每个测试运行之前，都会执行这个函数 """
    clean_all()


def test_password_hash():
    test_table = (
        "123123123",
        "15tyebsd1t2g",
        "&%^*TIYGF&68TYUFt*&t@#$"
        "!@#$%^&*()_+{''}:\"?<>"
        '"""""""""'
    )
    for pw in test_table:
        hpw = generate_password_hash(pw)
        assert hpw != generate_password_hash(pw)
        assert is_right_password(pw, hpw)


def test_constants_to_map():
    assert type(SEX_CHOICE) == tuple
    assert type(SEX_MAP) == dict
    for v, k in SEX_CHOICE:
        if v == 1:
            assert k == 'MALE'
        elif v == 0:
            assert k == "FEMALE"
    
    for v, k in SEX_MAP.items():
        if v == 1:
            assert k == 'MALE'
        elif v == 0:
            assert k == "FEMALE"


def test_contants_view():
    response = get_client().get("/v1/api/constants")
    assert response.status_code == 200


def test_jwt():
    table_data = (
        1,
        1523461,
        "asdfgwq",
        dict(a=1, b=2, c="123"),
        [1, 2, "123"]
    )
    for data in table_data:
        e = encode_token(data)
        er, ok = decode_token(e)
        assert ok
        assert er == data


def test_pagination():
    with get_session_local() as session:
        # session = TestingSessionLocal()
        for i in range(10):
            session.add(generate_role())
        session.commit()
        
        p1 = Pagination(session.query(RoleDB), 1, 5)
        assert p1.total == 10
        assert len(p1.items) == 5
        
        p2 = Pagination(session.query(RoleDB), 2, 5)
        assert p2.total == 10
        assert len(p2.items) == 5
        
        p3 = Pagination(session.query(RoleDB), 2, 8)
        assert p3.total == 10
        assert len(p3.items) == 2


def test_get_filename_without_uuid_prefix():
    raw_name = 'word.doc'
    temp_name = temp_file_name(raw_name)
    temp_name_with_path = f'temp/{temp_name}'
    assert raw_name == get_filename_without_uuid_prefix(temp_name_with_path)
