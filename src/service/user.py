from datetime import timedelta, datetime
import os
from jose import jwt
from jose.exceptions import JWTError
from model.user import User
from copy import deepcopy

from os import urandom

if os.getenv("CRYPTID_UNIT_TEST"):
    from fake import user as data
else:
    from data import user as data

# --- New auth stuff

import hashlib

# Change SECRET_KEY for production!
SECRET_KEY = "keep-it-secret-keep-it-safe"
ALGORITHM = "HS256"
N_ITER = 600000

def verify_password(name: str, plain: str) -> bool:
    """Hash <plain> and compare with <hash> from the database"""

    salt = data.get_user_salt(name=name)
    hash = data.get_hash_for_user(name)

    return hashlib.pbkdf2_hmac(
        password=plain.encode(encoding="utf-8"),
        hash_name='sha256',
        salt=salt.encode(encoding="utf-8"),
        iterations=N_ITER).hex() == hash

def get_hash(plain: str):
    """Return the hash of a <plain> string"""
    salt = urandom(16)
    return (
        hashlib.pbkdf2_hmac(
        password=plain.encode(encoding="utf-8"),
        hash_name='sha256',
        salt=salt,
        iterations=N_ITER).hex(),
        salt.hex()
    )

def get_jwt_username(token:str) -> str | None:
    """Return username from JWT access <token>"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not (username := payload.get("sub")):
            return None
    except JWTError:
        return None
    return username

def get_current_user(token: str) -> User | None:
    """Decode an OAuth access <token> and return the User"""
    if not (username := get_jwt_username(token)):
        return None
    if (user := lookup_user(username)):
        return user
    return None

def lookup_user(username: str) -> User | None:
    """Return a matching User from the database for <name>"""
    if (user := data.get_one(username)):
        return user
    return None

def auth_user(name: str, plain: str) -> User | None:
    """Authenticate user <name> and <plain> password"""
    if not (user := lookup_user(name)):
        return None
    if not verify_password(name, plain):
        return None
    return user

def create_access_token(data: dict,
    expires: timedelta | None = None
):
    """Return a JWT access token"""
    src = deepcopy(data)
    now = datetime.utcnow()
    if not expires:
        expires = timedelta(minutes=15)
    src.update({"exp": now + expires})
    encoded_jwt = jwt.encode(src, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- CRUD passthrough stuff

def get_all() -> list[User]:
    return data.get_all()

def get_one(name) -> User:
    return data.get_one(name)

def create(name: str, passwd: str) -> User:
    user = User(
        name=name, 
        hashed_passwd='',
        salt=''
    )
    user.hashed_passwd, user.salt = get_hash(user.hashed_passwd)

    return data.create(user)

def modify(name: str, passwd: str) -> User:
    return data.modify(name, passwd)

def delete(name: str) -> None:
    return data.delete(name)