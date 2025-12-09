from dataclasses import dataclass, field
from datetime import date

@dataclass
class ProdutoFornecedorModel:
    nome: str
    tipo: str | None = None
    intervalo_producao_inicio: date = None
    intervalo_producao_fim: date = None
    capacidade: int = 0