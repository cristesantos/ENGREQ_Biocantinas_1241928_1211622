from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class PlanoProducaoModel:
    """Model de domínio para PlanoProducao"""
    id: int
    periodo_data_inicio: date
    periodo_data_fim: date
    data_calculo: datetime
    produto_nome: str
    quantidade_prevista: int
    quantidade_realizada: int
    desvio_percentual: float
    requer_alerta: bool

    @property
    def desvio_percentual_formatado(self) -> str:
        """Formata o desvio percentual com sinal"""
        sinal = "+" if self.desvio_percentual > 0 else ""
        return f"{sinal}{self.desvio_percentual:.1f}%"

    @property
    def status(self) -> str:
        """Retorna status baseado no desvio"""
        if not self.requer_alerta:
            return "✅ OK"
        elif self.desvio_percentual > 0:
            return "⬆️ Excesso"
        else:
            return "⬇️ Falta"
