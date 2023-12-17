from fastapi import APIRouter, HTTPException
from model.creature import Creature
import data.creature as service
from data.errors import MissingException, DuplicateException

router = APIRouter(prefix = "/creature")

@router.get("")
@router.get("/")
def get_all() -> list[Creature]:
    return service.get_all()

@router.get("/{name}")
def get_one(name) -> Creature:
    try:
        return service.get_one(name)
    except MissingException as ex:
        raise HTTPException(
            status_code=404,
            detail=ex.msg
        )

@router.post("/")
def create(creature: Creature) -> Creature:
    try:
        return service.create(creature)
    except DuplicateException as ex:
        raise HTTPException(
            status_code=409,
            detail=ex.msg
        )

@router.patch("/")
def modify(creature: Creature) -> Creature:
    try:
        return service.modify(creature)
    except MissingException as ex:
        raise HTTPException(
            status_code=404,
            detail=ex.msg
        )

# @router.put("/")
# def replace(creature: Creature) -> Creature:
#     return service.replace(creature)

@router.delete("/{name}")
def delete(name: str):
    try:
        return service.delete(name)
    except MissingException as ex:
        raise HTTPException(
            status_code=404,
            detail=ex.msg
        )