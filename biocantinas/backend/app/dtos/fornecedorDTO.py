from pydantic import BaseModel
from datetime import date
from typing import List
from .produtoDTO import ProdutoFornecedorDTO

class FornecedorCreate(BaseModel):
	nome: str
	data_inscricao: date
	local: bool = False
	certificado: bool = False
	produtos: List[ProdutoFornecedorDTO]

class Fornecedor(FornecedorCreate):
	id: int
	aprovado: bool

class FornecedorUpdateAprovacao(BaseModel):
	aprovado: bool

class OrdemFornecedor(BaseModel):
	produto: str
	fornecedores_ids: List[int]
