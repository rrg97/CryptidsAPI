from fastapi import APIRouter, HTTPException
from model.explorer import Explorer
import data.explorer as service
from data.errors import MissingException, DuplicateException

router = APIRouter(
    prefix="/explorer"
)

@router.get("")
@router.get("/")
def get_all() -> list[Explorer]:
    return service.get_all()

@router.get("/{name}")
def get_one(name: str) -> Explorer | None:
    try:
        return service.get_one(name)
    except MissingException as ex:
        raise HTTPException(
            status_code=404,
            detail=ex.msg
        )

@router.post("/", status_code=201)
def create(explorer: Explorer) -> Explorer:
    try:
        return service.create(explorer)
    except DuplicateException as ex:
        raise HTTPException(
            status_code=409,
            detail=ex.msg
        )

@router.patch("/")
def modify(explorer: Explorer) -> Explorer:
    try:
        return service.modify(explorer)
    except MissingException as ex:
        raise HTTPException(
            status_code=404,
            detail=ex.msg
        )

# @router.put("/")
# def replace(explorer: Explorer) -> Explorer:
#     return service.replace(explorer)

@router.delete("/{name}")
def delete(name: str):
    try:
        return service.delete(name)
    except MissingException as ex:
        raise HTTPException(
            status_code=404,
            detail=ex.msg
        )