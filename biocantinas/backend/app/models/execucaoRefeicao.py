from dataclasses import dataclass
from datetime import date


@dataclass
class ExecucaoRefeicaoModel:
    id: int
    refeicao_id: int
    data_execucao: date
    quantidade_prevista: int | None = None  # Previsão do plano
    quantidade_produzida: int = 0
    quantidade_servida: int = 0
    quantidade_nao_servida: int = 0
    refeitorio_id: int | None = None
