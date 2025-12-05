from pydantic import BaseModel
from datetime import date

class ProdutoFornecedor(BaseModel):
	nome: str
	intervalo_producao_inicio: date
	intervalo_producao_fim: date
	capacidade: int
