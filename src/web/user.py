from datetime import timedelta
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from model.user import User
if os.getenv("CRYPTID_UNIT_TEST"):
    from fake import user as service
else:
    from service import user as service
from data.errors import MissingException, DuplicateException

ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_dep = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(prefix = "/user")


async def validate_token(request: Request):
    headers = request.headers
    if not headers["Authorization"]:
        raise HTTPException(
            status_code=422,
            detail="Missing authorization bearer token"
        )
    if headers["Authorization"].split(" ")[0] != "Bearer":
        raise HTTPException(
            status_code=422,
            detail="Bearer token type not specified"
        )

@router.get("/", dependencies=[Depends(validate_token)])
def get_all() -> list[User]:
    return service.get_all()

@router.get("/{name}", dependencies=[Depends(validate_token)])
def get_one(name) -> User:
    try:
        return service.get_one(name)
    except MissingException as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201, dependencies=[Depends(validate_token)])
def create(name: str, passwd: str) -> User:
    try:
        user = service.create(name, passwd)
        
        return User(
            name=name,
            hashed_passwd=user.hashed_passwd,
            salt=''
        )
    except DuplicateException as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/", dependencies=[Depends(validate_token)])
def modify(name: str, passwd: str) -> User:
    try:
        return service.modify(name, passwd)
    except MissingException as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{name}", dependencies=[Depends(validate_token)])
def delete(name: str) -> None:
    try:
        return service.delete(name)
    except MissingException as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

def unauthed():
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
        )

from main import app
@router.post("/token")
async def create_access_token(
    form_data: OAuth2PasswordRequestForm =  Depends()
):
    """Get username and password from OAuth form,
        return access token"""
    user = service.auth_user(form_data.username, form_data.password)
    if not user:
        unauthed()
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": user.name}, expires=expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token")
def get_access_token(token: str = Depends(oauth2_dep)) -> dict:
    """Return the current access token"""
    return {"token": token}