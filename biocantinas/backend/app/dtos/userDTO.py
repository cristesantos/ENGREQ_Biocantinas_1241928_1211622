from pydantic import BaseModel, Field
from enum import Enum


class User(BaseModel):
    id: int
    username: str
    role: str  # "ADMIN", "DIETISTA", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA", "GESTOR_REFEITORIO", "PRODUTOR" ou "FORNECEDOR"
    cantina_id: int | None = None
    refeitorio_id: int | None = None


class UserCreate(BaseModel):
    username: str
    password: str = Field(..., max_length=72, description="Password (max 72 characters due to bcrypt limitation)")
    role: str  # "ADMIN", "DIETISTA", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA", "GESTOR_REFEITORIO", "PRODUTOR" ou "FORNECEDOR"


class Role(str, Enum):
    admin = "ADMIN"
    dietista = "DIETISTA"
    gestor_cantina_central = "GESTOR_CANTINA_CENTRAL"
    gestor_cantina = "GESTOR_CANTINA"
    gestor_refeitorio = "GESTOR_REFEITORIO"
    produtor = "PRODUTOR"
    fornecedor = "FORNECEDOR"

class LoginRequest(BaseModel):
    username: str
    password: str = Field(..., max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"