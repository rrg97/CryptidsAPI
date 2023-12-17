from .init import conn, curs, IntegrityError
from model.creature import Creature
from .errors import MissingException, DuplicateException

curs.execute(
"""create table if not exists creature(
                name text primary key,
                description text,
                country text,
                area text,
                aka text)"""
)

def row_to_model(row: tuple) -> Creature:
    (name, description, country, area, aka) = row
    return Creature(name, description, country, area, aka)

def model_to_dict(creature: Creature) -> dict | None:
    return creature.model_dump() if creature else None

def get_one(name: str) -> Creature:
    if not name: return None

    qry = "select * from creature where name=:name"
    params = {"name": name}

    curs.execute(qry, params)
    row = row_to_model(curs.fetchone())
    
    if not row:
        raise MissingException(
            f"Creature {name} not found"
        )
    
    return row_to_model(curs.fetchone())

def get_all() -> list[Creature]:
    qry = "select * from creature"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]

def create(creature: Creature) -> Creature:
    if not creature: return None

    qry = "insert into creature values"
    "(:name, :description, :country, :area, :aka)"
    params = model_to_dict(creature)

    try:
        curs.execute(qry, params)
    except IntegrityError:
        raise DuplicateException(
            f"Creature {creature.name} already exists"
        )
    
    conn.commit()
    return get_one(creature.name)

def modify(creature: Creature) -> Creature:
    qry = """update creature
             set country=:country,
                 name=:name,
                 description=:description,
                 area=:area,
                 aka=:aka
             where name=:name_orig"""
    params = model_to_dict(creature)
    params["name_orig"] = creature.name
    curs.execute(qry, params)

    if curs.rowcount == 1:
        conn.commit()
        return get_one(creature.name)
    else:
        raise MissingException(msg=f"Creature {creature.name} not found")

def delete(name: str) -> bool:
    if not name: return False

    qry = "delete from creature where name = :name"
    params = {"name": name}
    curs.execute(qry, params)

    if curs.rowcount != 1:
        raise MissingException(
            f"Creature {name} not found"
        )
    conn.commit()
    
    return True