from pydantic import BaseModel, Field
from enum import Enum


class User(BaseModel):
    id: int
    username: str
    role: str  # "ADMIN", "DIETISTA", "GESTOR_CANTINA_CENTRAL", "PRODUTOR" or "FORNECEDOR"


class UserCreate(BaseModel):
    username: str
    password: str = Field(..., max_length=72, description="Password (max 72 characters due to bcrypt limitation)")
    role: str  # "ADMIN", "DIETISTA", "GESTOR_CANTINA_CENTRAL", "PRODUTOR" or "FORNECEDOR"


class Role(str, Enum):
    gestor = "gestor"
    produtor = "produtor"
    outro = "outro"

class LoginRequest(BaseModel):
    username: str
    password: str = Field(..., max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"