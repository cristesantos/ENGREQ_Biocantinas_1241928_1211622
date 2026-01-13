from pydantic import BaseModel
from datetime import date


class ExecucaoRefeicaoCreate(BaseModel):
    refeicao_id: int
    data_execucao: date
    quantidade_prevista: int | None = None  # Previsão do plano (opcional)
    quantidade_produzida: int
    quantidade_servida: int
    quantidade_nao_servida: int
    refeitorio_id: int | None = None


class ExecucaoRefeicao(BaseModel):
    id: int
    refeicao_id: int
    data_execucao: date
    quantidade_prevista: int | None = None
    quantidade_produzida: int
    quantidade_servida: int
    quantidade_nao_servida: int
    refeitorio_id: int | None = None
