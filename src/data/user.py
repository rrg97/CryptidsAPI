from model.user import User
from .init import (conn, curs, IntegrityError)
from .errors import MissingException, DuplicateException

curs.execute("""create table if not exists
                user(
                  name text primary key,
                  hashed_passwd text, salt bytes)""")
curs.execute("""create table if not exists
                xuser(
                  name text primary key,
                  hashed_passwd text, salt bytes)""")

def row_to_model(row: tuple) -> User:
    name, hashed_passwd, salt = row
    return User(name=name, hashed_passwd=hashed_passwd, salt= salt)

def model_to_dict(user: User) -> dict | None:
    return user.model_dump() if user else None

def get_user_salt(name: str) -> str:
    qry = "select salt from user where name=:name"
    params = {"name": name}
    curs.execute(qry, params)
    row = curs.fetchone()

    return row[0]

def get_hash_for_user(name: str) -> str:
    qry = "select hashed_passwd from user where name=:name"
    params = {"name": name}
    curs.execute(qry, params)
    row = curs.fetchone()

    return row[0]

def get_one(name: str) -> User:
    qry = "select * from user where name=:name"
    params = {"name": name}
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise MissingException(msg=f"User {name} not found")

def get_all() -> list[User]:
    qry = "select * from user"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]

def create(user: User, table:str = "user"):
    qry = f"""insert into {table}
        (name, hashed_passwd, salt)
        values
        (:name, :hashed_passwd, :salt)"""
    params = model_to_dict(user)
    try:
        curs.execute(qry, params)
        conn.commit()
        return user
    except IntegrityError:
        raise DuplicateException(msg=
            f"{table}: user {user.name} already exists")

def modify(name: str, passwd: str)  -> User:
    qry = """update user set
             name=:name, hashed_passwd=:hashed_passwd
             where name=:name0"""
    params = {
        "name": name,
        "hashed_passwd": passwd,
        "name0": name}
    curs.execute(qry, params)
    conn.commit()
    if curs.rowcount == 1:
        return get_one(name)
    else:
        raise MissingException(msg=f"User {name} not found")

def delete(name: str) -> None:
    """Drop user with <name> from user table, add to xuser table"""
    user = get_one(name)
    qry = "delete from user where name = :name"
    params = {"name": name}
    curs.execute(qry, params)
    conn.commit()
    if curs.rowcount != 1:
        raise MissingException(msg=f"User {name} not found")
    create(user, table="xuser")