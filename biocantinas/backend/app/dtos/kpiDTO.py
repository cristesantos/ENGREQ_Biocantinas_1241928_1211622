from pydantic import BaseModel
from typing import List, Optional

class IngredienteKPIDTO(BaseModel):
    nome: str
    biologico: bool
    fornecedor_id: Optional[int] = None

class RefeicaoKPIDTO(BaseModel):
    refeicao_id: int
    refeicao_descricao: str
    total_ingredientes: int
    ingredientes_biologicos: int
    percentagem_biologica: float
    ingredientes: List[IngredienteKPIDTO]

class DiaKPIDTO(BaseModel):
    ementa_id: int
    dia_semana: int
    percentagem_biologica_almoco: float
    percentagem_biologica_jantar: float
    media_percentagem_biologica: float

class EmentaKPIDTO(BaseModel):
    ementa_id: int
    ementa_nome: str
    media_percentagem_biologica: float
    dias: List[DiaKPIDTO]

# ==== KPIs DE DESPERDÍCIO ====

class DesperdícioRefeicaoDTO(BaseModel):
    refeicao_id: int
    refeicao_descricao: str
    data_execucao: str
    quantidade_produzida: int
    quantidade_servida: int
    quantidade_nao_servida: int
    taxa_desperdicio: float  # % de nao_servida / produzida
    taxa_servida: float  # % de servida / produzida

class DesperdícioDiaDTO(BaseModel):
    ementa_id: int
    dia_semana: int
    tipo_refeicao: str  # "almoço" ou "jantar"
    total_produzido: int
    total_servido: int
    total_nao_servido: int
    taxa_desperdicio_media: float  # % média de desperdício
    taxa_servida_media: float  # % média servida

class DesperdícioEmentaDTO(BaseModel):
    ementa_id: int
    ementa_nome: str
    total_produzido: int
    total_servido: int
    total_nao_servido: int
    taxa_desperdicio_geral: float  # % média de desperdício na semana
    taxa_servida_geral: float  # % média servida
    dias: List[DesperdícioDiaDTO]

# ==== KPI CONSOLIDADO (BIOLÓGICO + DESPERDÍCIO) ====

class KPIConsolidadoDTO(BaseModel):
    ementa_id: int
    ementa_nome: str
    # Biológico
    percentagem_biologica: float
    # Desperdício
    taxa_desperdicio: float
    taxa_servida: float
    # Resumo
    total_produzido: int
    total_servido: int
    total_nao_servido: int
