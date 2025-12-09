from pydantic import BaseModel
from datetime import date, datetime

# Reservas de Refeições
class ReservaRefeicaoCreate(BaseModel):
    refeicao_id: int
    quantidade_pessoas: int = 1

class ReservaRefeicaoDTO(ReservaRefeicaoCreate):
    id: int
    utilizador_id: int
    data_reserva: datetime

    class Config:
        from_attributes = True


# Plano de Produção
class PlanoProducaoDTO(BaseModel):
    id: int
    data_calculo: datetime
    produto_nome: str
    quantidade_prevista: int
    quantidade_realizada: int
    desvio_percentual: float
    requer_alerta: bool

    class Config:
        from_attributes = True


# Pedidos aos Fornecedores
class PedidoFornecedorCreate(BaseModel):
    fornecedor_id: int
    produto_id: int
    quantidade_solicitada: int
    data_entrega_prevista: date

class PedidoFornecedorDTO(PedidoFornecedorCreate):
    id: int
    data_pedido: datetime
    status: str
    ordem_prioridade: int

    class Config:
        from_attributes = True


# Preview de Necessidades (para visualização)
class PreviewNecessidadesDTO(BaseModel):
    periodo: str
    necessidades_planejadas: dict[str, int]
    necessidades_com_reservas: dict[str, int]
    desvios: dict[str, float]
