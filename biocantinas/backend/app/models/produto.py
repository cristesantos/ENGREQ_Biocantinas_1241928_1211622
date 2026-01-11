from dataclasses import dataclass, field
from datetime import date

@dataclass
class ProdutoFornecedorModel:
    """Produto de um fornecedor específico (referência ao catálogo global)"""
    fornecedor_id: int
    produto_id: int
    capacidade: int
    semana_producao_inicio: int  # Semana do ano (1-52)
    semana_producao_fim: int  # Semana do ano (1-52)
    id: int = 0
    preco_unitario: float | None = None
    unidade_medida: str | None = None
    biologico: bool = True
    certificado: str | None = None
    data_inscricao: date = field(default_factory=date.today)
    
    # Dados do produto (desnormalizados para facilitar)
    nome: str | None = None
    tipo: str | None = None


@dataclass
class ProdutoModel:
    """Model para produto do catálogo"""
    nome: str
    tipo: str | None = None
    descricao: str | None = None
    unidade_medida: str = "kg"
    epoca_tipica: str | None = None
    ativo: bool = True
    id: int = 0