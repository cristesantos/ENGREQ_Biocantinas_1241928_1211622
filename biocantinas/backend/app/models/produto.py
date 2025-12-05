from dataclasses import dataclass, field
from datetime import date

@dataclass
class ProdutoFornecedorModel:
    nome: str
    intervalo_producao_inicio: date
    intervalo_producao_fim: date
    capacidade: int