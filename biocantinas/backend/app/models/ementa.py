from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class ItemRefeicaoModel:
    ingrediente: str
    produto_id: int | None = None
    quantidade_estimada: float | None = None
    unidade_medida: str | None = None


@dataclass
class RefeicaoModel:
    dia_semana: int  # 1=Segunda, 2=Terça, 3=Quarta, 4=Quinta, 5=Sexta
    tipo: str  # "almoço" ou "jantar"
    descricao: str | None = None
    itens: List[ItemRefeicaoModel] = field(default_factory=list)
    receita_id: int | None = None  # Referência à receita do catálogo
    numero_porcoes: int | None = None  # Número de porções planejadas
    id: int | None = None  # ID da refeição (apenas quando recuperada da BD)


@dataclass
class EmentaModel:
    id: int
    nome: str
    data_inicio: date
    data_fim: date
    refeicoes: List[RefeicaoModel] = field(default_factory=list)
