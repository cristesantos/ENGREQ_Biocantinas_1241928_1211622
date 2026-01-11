from pydantic import BaseModel, field_validator, Field
from datetime import date
from typing import List
from .produtoDTO import ProdutoFornecedor

class FornecedorCreate(BaseModel):
	nome: str
	data_inscricao: date
	produtos: List[ProdutoFornecedor]
	local: bool = False
	certificado: bool = False
	freguesia: str | None = None
	em_quarentena: bool = False

class Fornecedor(FornecedorCreate):
	id: int
	aprovado: bool

class FornecedorUpdateAprovacao(BaseModel):
	aprovado: bool

class FornecedorEstadoUpdate(BaseModel):
	em_quarentena: bool | None = None
	freguesia: str | None = None

class FreguesiaFecho(BaseModel):
	nome: str
	ativo: bool = True

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
		if 'semana_producao_inicio' in info.data:
			inicio = info.data['semana_producao_inicio']
			# Permitir intervalos circulares (ex.: 11-9) para representar faixas que cruzam o fim do ano
			if inicio is None:
				return v
			if inicio <= v or inicio > v:
				return v
		return v

class OrdemFornecedor(BaseModel):
	produto: str
	fornecedores_ids: List[int]
