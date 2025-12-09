from pydantic import BaseModel
from datetime import date
from typing import List


class ItemRefeicao(BaseModel):
    ingrediente: str
    produto_id: int | None = None
    quantidade_estimada: int | None = None


class Refeicao(BaseModel):
    dia_semana: int  # 1=Segunda, 2=Terça, 3=Quarta, 4=Quinta, 5=Sexta
    tipo: str  # "almoço" ou "jantar"
    descricao: str | None = None
    itens: List[ItemRefeicao] = []


class EmentaCreate(BaseModel):
    nome: str
    data_inicio: date
    data_fim: date
    refeicoes: List[Refeicao] = []


class Ementa(EmentaCreate):
    id: int
