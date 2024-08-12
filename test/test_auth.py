from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from fastapi import HTTPException
from jose import jwt
from datetime import timedelta
import pytest

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.user_name, 'string', db)
    assert authenticated_user is not None
    assert authenticated_user.user_name == test_user.user_name

    non_user = authenticate_user('not an user', 'string', db)
    assert non_user is False

    wrong_password = authenticate_user(test_user.user_name, 'wrong string', db)
    assert wrong_password is False

def test_create_access_token(test_user):
    user_name = 'username'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(user_name, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == user_name
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {
        'sub':'testuser',
        'id': 1,
        'role': 'admin'
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {
        'username':'testuser',
        'id': 1,
        'role': 'admin'
    }

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {
        'role': 'user'
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'