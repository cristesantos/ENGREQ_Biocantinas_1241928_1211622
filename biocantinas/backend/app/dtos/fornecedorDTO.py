from pydantic import BaseModel, field_validator, Field
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
	unidade: str = "kg"
	certificado: str | None = None
	data_inscricao: date = Field(default_factory=date.today)
	
	@field_validator('semana_producao_inicio', 'semana_producao_fim')
	@classmethod
	def validar_semanas(cls, v):
		if not (1 <= v <= 52):
			raise ValueError('Semana deve estar entre 1 e 52')
		return v
	
	@field_validator('semana_producao_fim')
	@classmethod
	def validar_fim_maior_que_inicio(cls, v, info):
		if 'semana_producao_inicio' in info.data and v < info.data['semana_producao_inicio']:
			raise ValueError('Semana fim deve ser maior ou igual à semana início')
		return v

class OrdemFornecedor(BaseModel):
	produto: str
	fornecedores_ids: List[int]
