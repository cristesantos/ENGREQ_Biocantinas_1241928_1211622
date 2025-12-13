from dataclasses import dataclass
from datetime import date


@dataclass
class ExecucaoRefeicaoModel:
    id: int
    refeicao_id: int
    data_execucao: date
    quantidade_produzida: int
    quantidade_servida: int
    quantidade_nao_servida: int
