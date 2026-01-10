from dataclasses import dataclass, field
from datetime import date

@dataclass
class ProdutoFornecedorModel:
    nome: str
    semana_producao_inicio: int
    semana_producao_fim: int
    capacidade: int
    tipo: str | None = None
    biologico: bool = True
    unidade: str = "kg"
    certificado: str | None = None