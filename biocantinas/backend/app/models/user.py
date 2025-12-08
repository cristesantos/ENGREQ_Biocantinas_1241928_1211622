from dataclasses import dataclass


@dataclass
class UserModel:
    id: int
    username: str
    password_hash: str
    role: str  # "GESTOR" or "PRODUTOR"