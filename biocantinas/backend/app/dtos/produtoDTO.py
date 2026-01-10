from pydantic import BaseModel, field_validator, Field
from datetime import date

class ProdutoFornecedor(BaseModel):
	nome: str
	tipo: str | None = None
	biologico: bool = True
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


class ProdutoCreateDTO(BaseModel):
	"""DTO para criar um produto individualmente"""
	nome: str
	tipo: str | None = None
	biologico: bool = True
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


class ProdutoUpdateDTO(BaseModel):
	"""DTO para atualizar um produto"""
	nome: str
	tipo: str | None = None
	biologico: bool = True
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
	unidade: str = "kg"
	certificado: str | None = None
	data_inscricao: date
	
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