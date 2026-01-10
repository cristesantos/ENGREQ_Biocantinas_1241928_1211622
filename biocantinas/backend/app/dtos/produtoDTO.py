from pydantic import BaseModel
from datetime import date
from typing import Optional

# ============ DTOs para Produto (Catálogo Global) ============

class ProdutoCatalogoCreateDTO(BaseModel):
	"""DTO para criar um produto no catálogo global"""
	nome: str
	tipo: Optional[str] = None
	descricao: Optional[str] = None
	unidade_medida: Optional[str] = None
	epoca_tipica: Optional[str] = None
	ativo: bool = True


class ProdutoCatalogoUpdateDTO(BaseModel):
	"""DTO para atualizar um produto do catálogo"""
	nome: Optional[str] = None
	tipo: Optional[str] = None
	descricao: Optional[str] = None
	unidade_medida: Optional[str] = None
	epoca_tipica: Optional[str] = None
	ativo: Optional[bool] = None


class ProdutoCatalogoDTO(BaseModel):
	"""DTO completo de produto do catálogo"""
	id: int
	nome: str
	tipo: Optional[str] = None
	descricao: Optional[str] = None
	unidade_medida: Optional[str] = None
	epoca_tipica: Optional[str] = None
	ativo: bool = True


# ============ DTOs para ProdutoFornecedor ============

class ProdutoFornecedorDTO(BaseModel):
	"""DTO básico para produto de fornecedor"""
	produto_id: int
	preco_unitario: Optional[float] = None
	capacidade: int
	unidade_medida: Optional[str] = None
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	prioridade: int = 1
	biologico: bool = False
	disponivel: bool = True



class ProdutoFornecedorCreateDTO(BaseModel):
	"""DTO para criar um produto de fornecedor"""
	produto_id: int
	preco_unitario: Optional[float] = None
	capacidade: int
	unidade_medida: Optional[str] = None
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	prioridade: int = 1
	biologico: bool = False
	disponivel: bool = True




class ProdutoFornecedorUpdateDTO(BaseModel):
	"""DTO para atualizar um produto de fornecedor"""
	produto_id: Optional[int] = None
	preco_unitario: Optional[float] = None
	capacidade: Optional[int] = None
	unidade_medida: Optional[str] = None
	intervalo_producao_inicio: Optional[date] = None
	intervalo_producao_fim: Optional[date] = None
	prioridade: Optional[int] = None
	biologico: Optional[bool] = None
	disponivel: Optional[bool] = None


 


class ProdutoDTO(BaseModel):
	"""DTO completo de produto de fornecedor com informações do catálogo"""
	id: int
	fornecedor_id: int
	produto_id: int
	produto_nome: str  # Nome do produto do catálogo
	produto_tipo: Optional[str] = None  # Tipo do produto do catálogo
	preco_unitario: Optional[float] = None
	capacidade: int
	unidade_medida: Optional[str] = None
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	prioridade: int = 1
	biologico: bool = False
	disponivel: bool = True