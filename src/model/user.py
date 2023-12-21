from pydantic import BaseModel

class User(BaseModel):
    name: str
    hashed_passwd: str
    salt: bytes