from pydantic import BaseModel
from datetime import date


class ExecucaoRefeicaoCreate(BaseModel):
    refeicao_id: int
    data_execucao: date
    quantidade_produzida: int
    quantidade_servida: int
    quantidade_nao_servida: int


class ExecucaoRefeicao(BaseModel):
    id: int
    refeicao_id: int
    data_execucao: date
    quantidade_produzida: int
    quantidade_servida: int
    quantidade_nao_servida: int
