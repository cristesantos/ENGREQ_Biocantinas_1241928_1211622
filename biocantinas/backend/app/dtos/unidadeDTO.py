from pydantic import BaseModel
from typing import Optional


class CantinaBase(BaseModel):
    nome: str
    localizacao: Optional[str] = None
    tipo: str = "CENTRAL"  # CENTRAL ou LOCAL
    gestor_id: Optional[int] = None


class CantinaCreate(CantinaBase):
    pass


class Cantina(CantinaBase):
    id: int

    class Config:
        orm_mode = True


class RefeitorioBase(BaseModel):
    nome: str
    localizacao: Optional[str] = None
    gestor_id: Optional[int] = None
    cantina_id: Optional[int] = None


class RefeitorioCreate(RefeitorioBase):
    pass


class Refeitorio(RefeitorioBase):
    id: int

    class Config:
        orm_mode = True
