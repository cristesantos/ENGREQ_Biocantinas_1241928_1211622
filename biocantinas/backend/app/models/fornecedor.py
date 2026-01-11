from dataclasses import dataclass, field
from datetime import date
from typing import List
from .produto import ProdutoFornecedorModel


@dataclass
class FornecedorModel:
    id: int
    nome: str
    data_inscricao: date
    produtos: List[ProdutoFornecedorModel] = field(default_factory=list)
    aprovado: bool = False
    local: bool = False
    certificado: bool = False
    usuario_id: int | None = None  # Vínculo com o usuário
    em_quarentena: bool = False
    freguesia: str | None = None
