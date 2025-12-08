from pydantic import BaseModel
from enum import Enum


class User(BaseModel):
    id: int
    username: str
    role: str  # "GESTOR" or "PRODUTOR"


class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # "GESTOR" or "PRODUTOR"


class Role(str, Enum):
    gestor = "gestor"
    produtor = "produtor"
    outro = "outro"

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"