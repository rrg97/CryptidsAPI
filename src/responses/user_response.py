from pydantic import BaseModel

class UserResponse(BaseModel):
    name: str
    hashed_passwd: str