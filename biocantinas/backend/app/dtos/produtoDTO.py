from pydantic import BaseModel
from datetime import date

class ProdutoFornecedor(BaseModel):
	nome: str
	tipo: str | None = None
	biologico: bool = True
	semana_producao_inicio: int
	semana_producao_fim: int
	capacidade: int
	certificado: str | None = None


class ProdutoCreateDTO(BaseModel):
	"""DTO para criar um produto individualmente"""
	nome: str
	tipo: str | None = None
	biologico: bool = True
	semana_producao_inicio: int
	semana_producao_fim: int
	capacidade: int
	certificado: str | None = None


class ProdutoUpdateDTO(BaseModel):
	"""DTO para atualizar um produto"""
	nome: str
	tipo: str | None = None
	biologico: bool = True
	semana_producao_inicio: int
	semana_producao_fim: int
	capacidade: int
	certificado: str | None = None


class ProdutoDTO(BaseModel):
	"""DTO completo de produto com ID e fornecedor_id"""
	id: int
	fornecedor_id: int
	nome: str
	tipo: str | None = None
	biologico: bool = True
	semana_producao_inicio: int
	semana_producao_fim: int
	capacidade: int
	certificado: str | None = None