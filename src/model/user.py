from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: str
    hashed_passwd: str
    salt: str