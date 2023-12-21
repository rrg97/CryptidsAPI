from datetime import timedelta
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from model.user import User
from responses import UserResponse

if os.getenv("CRYPTID_UNIT_TEST"):
    from fake import user as service
else:
    from service import user as service
from data.errors import MissingException, DuplicateException

ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_dep = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(prefix = "/user")


async def is_valid_token(request: Request):
    headers = request.headers
    if "Authorization" not in headers:
        raise HTTPException(
            status_code=422,
            detail="Missing authorization bearer token"
        )
    token_type, token = headers["Authorization"].split(" ")
    if token_type != "Bearer":
        raise HTTPException(
            status_code=422,
            detail="Bearer token type not specified"
        )
    
    username: str = service.get_jwt_username(token=token)

    return username is not None

@router.get("/", response_model=list[UserResponse])
def get_all(valid_token: bool = Depends(is_valid_token)) -> list[UserResponse]:
    if not valid_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization bearer token"
        )
    users = service.get_all()
    users_ = [UserResponse(**user.model_dump()) for user in users]

    return users_

@router.get("/{name}", response_model=UserResponse)
def get_one(name: str, valid_token: bool = Depends(is_valid_token)) -> UserResponse:
    if not valid_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization bearer token"
        )
    try:
        user = service.get_one(name)
        return UserResponse(
            name=user.name,
            hashed_passwd=user.hashed_passwd
        )
    except MissingException as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201, dependencies=[Depends(is_valid_token)], response_model=UserResponse)
def create(name: str, passwd: str) -> UserResponse:
    try:
        user = service.create(name, passwd)
        
        return UserResponse(
            name=name,
            hashed_passwd=user.hashed_passwd,
        )
    except DuplicateException as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/", dependencies=[Depends(is_valid_token)], response_model=UserResponse)
def modify(name: str, passwd: str) -> UserResponse:
    try:
        user = service.modify(name, passwd)

        return UserResponse(
            name=user.name,
            hashed_passwd=user.hashed_passwd
        )
    except MissingException as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{name}", dependencies=[Depends(is_valid_token)], response_model=UserResponse)
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

from main import app
@app.post("/token")
def get_access_token(token: str = Depends(oauth2_dep)) -> dict:
    """Return the current access token"""
    return {"token": token}