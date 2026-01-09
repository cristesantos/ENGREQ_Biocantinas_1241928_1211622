from dataclasses import dataclass, field
from datetime import date

@dataclass
class ProdutoFornecedorModel:
    nome: str
    tipo: str | None = None
    biologico: bool = True
    semana_producao_inicio: int = None
    semana_producao_fim: int = None
    capacidade: int = 0
    certificado: str | None = None