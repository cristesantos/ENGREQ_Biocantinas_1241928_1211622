from pydantic import BaseModel
from datetime import date
from typing import List
from .produtoDTO import ProdutoFornecedor

class FornecedorCreate(BaseModel):
	nome: str
	data_inscricao: date
	produtos: List[ProdutoFornecedor]

class Fornecedor(FornecedorCreate):
	id: int
	aprovado: bool

class FornecedorUpdateAprovacao(BaseModel):
	aprovado: bool

class ProdutoFornecedorAdd(BaseModel):
	"""DTO para adicionar um novo produto a um fornecedor existente"""
	nome: str
	biologico: bool
	semana_producao_inicio: int
	semana_producao_fim: int
	capacidade: int
	certificado: str | None = None

class OrdemFornecedor(BaseModel):
	produto: str
	fornecedores_ids: List[int]
