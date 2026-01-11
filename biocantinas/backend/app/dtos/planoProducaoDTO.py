from pydantic import BaseModel
from datetime import date, datetime


class PlanoProducaoBase(BaseModel):
    """Base DTO para PlanoProducao com dados comuns"""
    periodo_data_inicio: date
    periodo_data_fim: date
    produto_nome: str
    quantidade_prevista: int
    quantidade_realizada: int = 0
    desvio_percentual: float = 0.0
    requer_alerta: bool = False


class PlanoProducaoCreate(PlanoProducaoBase):
    """DTO para criar um novo PlanoProducao"""
    pass


class PlanoProducaoUpdate(BaseModel):
    """DTO para atualizar PlanoProducao"""
    quantidade_realizada: int | None = None
    desvio_percentual: float | None = None
    requer_alerta: bool | None = None


class PlanoProducaoResponse(PlanoProducaoBase):
    """DTO para resposta de PlanoProducao"""
    id: int
    data_calculo: datetime

    class Config:
        from_attributes = True


class PlanoProducaoSumario(BaseModel):
    """Sumário simplificado para listas"""
    periodo_data_inicio: date
    periodo_data_fim: date
    produto_nome: str
    quantidade_prevista: int
    quantidade_realizada: int
    desvio_percentual: float
    status: str  # "OK", "Alerta", etc.

    class Config:
        from_attributes = True
