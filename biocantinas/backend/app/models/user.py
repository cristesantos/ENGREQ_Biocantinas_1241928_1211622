from dataclasses import dataclass


@dataclass
class UserModel:
    id: int
    username: str
    password_hash: str
    role: str  # "ADMIN", "DIETISTA", "GESTOR_CANTINA_CENTRAL", "PRODUTOR" or "FORNECEDOR"