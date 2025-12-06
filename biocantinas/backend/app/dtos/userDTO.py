from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    role: str  # "GESTOR" or "PRODUTOR"


class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # "GESTOR" or "PRODUTOR"
