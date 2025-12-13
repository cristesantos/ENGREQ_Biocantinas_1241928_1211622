from pydantic import BaseModel
from datetime import date

class ProdutoFornecedor(BaseModel):
	nome: str
	tipo: str | None = None
	biologico: bool = True
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	capacidade: int


class ProdutoCreateDTO(BaseModel):
	"""DTO para criar um produto individualmente"""
	nome: str
	tipo: str | None = None
	biologico: bool = True
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	capacidade: int


class ProdutoUpdateDTO(BaseModel):
	"""DTO para atualizar um produto"""
	nome: str
	tipo: str | None = None
	biologico: bool = True
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	capacidade: int


class ProdutoDTO(BaseModel):
	"""DTO completo de produto com ID e fornecedor_id"""
	id: int
	fornecedor_id: int
	nome: str
	tipo: str | None = None
	biologico: bool = True
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	capacidade: int