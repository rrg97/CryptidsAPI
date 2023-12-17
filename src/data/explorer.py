from .init import curs, conn, IntegrityError
from model.explorer import Explorer
from .errors import MissingException, DuplicateException

curs.execute("""create table if not exists explorer(
                name text primary key,
                country text,
                description text)""")

def row_to_model(row: tuple) -> Explorer:
    return Explorer(name=row[0], country=row[1], description=row[2])

def model_to_dict(explorer: Explorer) -> dict | None:
    return explorer.model_dump() if explorer else None

def get_one(name: str) -> Explorer:
    if not name: return None

    qry = "select * from explorer where name=:name"
    params = {"name": name}
    curs.execute(qry, params)

    row = row_to_model(curs.fetchone())
    if not row:
        raise MissingException(
            f"Explorer {name} not found"
        )

    return row

def get_all() -> list[Explorer]:
    qry = "select * from explorer"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]

def create(explorer: Explorer) -> Explorer | None:
    if not explorer: return None
    qry = """insert into explorer (name, country, description)
             values (:name, :country, :description)"""
    params = model_to_dict(explorer)

    try:
        curs.execute(qry, params)
    except IntegrityError:
        raise DuplicateException(
            f"Explorer {explorer.name} already exists"
        )
    
    conn.commit()

    return get_one(explorer.name)

def modify(explorer: Explorer) -> Explorer | None:
    if not explorer: return None
    qry = """update explorer
             set country=:country,
             name=:name,
             description=:description
             where name=:name_orig"""
    params = model_to_dict(explorer)
    params["name_orig"] = explorer.name
    curs.execute(qry, params)
    
    if curs.rowcount == 1:
        conn.commit()
        return get_one(explorer.name)
    else:
        raise MissingException(msg=f"Explorer {explorer.name} not found")

def delete(name: str) -> bool:
    if not name: return False

    qry = "delete from explorer where name = :name"
    params = {"name": name}
    curs.execute(qry, params)

    if curs.rowcount != 1:
        raise MissingException(
            f"Explorer {name} not found"
        )
    conn.commit()
    
    return True