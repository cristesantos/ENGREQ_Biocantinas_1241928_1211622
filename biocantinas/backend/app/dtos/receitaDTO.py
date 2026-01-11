"""
DTOs para Receitas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ItemReceitaDTO(BaseModel):
    """Ingrediente de uma receita"""
    id: Optional[int] = None
    produto_catalogo_id: int
    produto_nome: Optional[str] = None
    quantidade_por_porcao: float = Field(..., gt=0, description="Quantidade por porção na unidade do produto")
    unidade_medida: Optional[str] = None

    class Config:
        from_attributes = True


class ReceitaDTO(BaseModel):
    """Receita completa do catálogo"""
    id: int
    nome: str
    descricao: Optional[str] = None
    tipo_refeicao: Optional[str] = None
    categoria: Optional[str] = None
    porcoes_base: int = 1
    tempo_preparo: Optional[int] = None
    ativa: bool = True
    ingredientes: List[ItemReceitaDTO] = []

    class Config:
        from_attributes = True


class ReceitaCreateDTO(BaseModel):
    """DTO para criar uma nova receita"""
    nome: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = None
    tipo_refeicao: Optional[str] = Field(None, pattern="^(almoço|jantar|ambos)$")
    categoria: Optional[str] = None
    porcoes_base: int = Field(1, gt=0)
    tempo_preparo: Optional[int] = Field(None, ge=0)
    ativa: bool = True
    ingredientes: List[ItemReceitaDTO] = Field(..., min_length=1)

    class Config:
        from_attributes = True


class ReceitaUpdateDTO(BaseModel):
    """DTO para atualizar uma receita existente"""
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = None
    tipo_refeicao: Optional[str] = Field(None, pattern="^(almoço|jantar|ambos)$")
    categoria: Optional[str] = None
    porcoes_base: Optional[int] = Field(None, gt=0)
    tempo_preparo: Optional[int] = Field(None, ge=0)
    ativa: Optional[bool] = None
    ingredientes: Optional[List[ItemReceitaDTO]] = None

    class Config:
        from_attributes = True
