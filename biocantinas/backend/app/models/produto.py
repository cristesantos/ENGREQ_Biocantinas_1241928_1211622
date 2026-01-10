from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class ProdutoModel:
	"""Produto do catálogo global"""
	id: int
	nome: str
	tipo: Optional[str] = None
	descricao: Optional[str] = None
	unidade_medida: Optional[str] = None
	epoca_tipica: Optional[str] = None
	ativo: bool = True


@dataclass
class ProdutoFornecedorModel:
	"""Produto de um fornecedor específico"""
	produto_id: int
	capacidade: int
	intervalo_producao_inicio: Optional[date] = None
	intervalo_producao_fim: Optional[date] = None
	id: int = 0
	fornecedor_id: int = 0
	produto_nome: str = ""
	produto_tipo: Optional[str] = None
	preco_unitario: Optional[float] = None
	unidade_medida: Optional[str] = None
	prioridade: int = 1
	biologico: bool = False
	disponivel: bool = True