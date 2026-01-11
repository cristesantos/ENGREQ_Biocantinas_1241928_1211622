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


class ProdutoCatalogoDTO(BaseModel):
	"""DTO para produto do catálogo global"""
	id: int
	nome: str
	tipo: str | None = None
	descricao: str | None = None
	unidade_medida: str = "kg"
	epoca_tipica: str | None = None
	ativo: bool = True


class ProdutoCatalogoCreateDTO(BaseModel):
	"""DTO para criar produto no catálogo"""
	nome: str
	tipo: str | None = None
	descricao: str | None = None
	unidade_medida: str = "kg"
	epoca_tipica: str | None = None
	ativo: bool = True


class ProdutoCatalogoUpdateDTO(BaseModel):
	"""DTO para atualizar produto no catálogo"""
	nome: str | None = None
	tipo: str | None = None
	descricao: str | None = None
	unidade_medida: str | None = None
	epoca_tipica: str | None = None
	ativo: bool | None = None


class ProdutoFornecedorDTO(BaseModel):
	"""DTO para produto de fornecedor"""
	id: int
	fornecedor_id: int
	produto_id: int
	capacidade: int
	preco_unitario: float | None = None
	unidade_medida: str = "kg"
	intervalo_producao_inicio: int | None = None
	intervalo_producao_fim: int | None = None
	prioridade: int | None = None
	biologico: bool = True
	local: bool = False
	disponivel: bool = True


class ProdutoFornecedorCreateDTO(BaseModel):
	"""DTO para criar produto em fornecedor"""
	produto_id: int
	capacidade: int
	preco_unitario: float | None = None
	unidade_medida: str = "kg"
	intervalo_producao_inicio: int | None = None
	intervalo_producao_fim: int | None = None
	prioridade: int | None = None
	biologico: bool = True
	local: bool = False
	disponivel: bool = True


class ProdutoFornecedorUpdateDTO(BaseModel):
	"""DTO para atualizar produto em fornecedor"""
	produto_id: int | None = None
	capacidade: int | None = None
	preco_unitario: float | None = None
	unidade_medida: str | None = None
	intervalo_producao_inicio: int | None = None
	intervalo_producao_fim: int | None = None
	prioridade: int | None = None
	biologico: bool | None = None
	local: bool | None = None
	disponivel: bool | None = None