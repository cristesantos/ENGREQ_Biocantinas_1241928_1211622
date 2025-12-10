from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class FornecedorORM(Base):
    __tablename__ = "fornecedores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    data_inscricao = Column(Date, nullable=False)
    aprovado = Column(Boolean, default=False, nullable=False)

    produtos = relationship("ProdutoFornecedorORM", back_populates="fornecedor", cascade="all, delete-orphan")

class ProdutoFornecedorORM(Base):
    __tablename__ = "produtos_fornecedor"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=True)  # Categoria do produto: fruta, hortícola, proteína, etc.
    intervalo_producao_inicio = Column(Date, nullable=False)
    intervalo_producao_fim = Column(Date, nullable=False)
    capacidade = Column(Integer, nullable=False)

    fornecedor = relationship("FornecedorORM", back_populates="produtos")

class UserORM(Base):
    __tablename__ = "utilizadores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class EmentaORM(Base):
    __tablename__ = "ementas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    
    refeicoes = relationship("RefeicaoORM", back_populates="ementa", cascade="all, delete-orphan")


class RefeicaoORM(Base):
    __tablename__ = "refeicoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ementa_id = Column(Integer, ForeignKey("ementas.id"), nullable=False)
    dia_semana = Column(Integer, nullable=False)  # 1=Segunda, 2=Terça, ..., 5=Sexta
    tipo = Column(String, nullable=False)  # "almoço" ou "jantar"
    descricao = Column(Text, nullable=True)
    
    ementa = relationship("EmentaORM", back_populates="refeicoes")
    itens = relationship("ItemRefeicaoORM", back_populates="refeicao", cascade="all, delete-orphan")


class ItemRefeicaoORM(Base):
    __tablename__ = "itens_refeicao"
    id = Column(Integer, primary_key=True, autoincrement=True)
    refeicao_id = Column(Integer, ForeignKey("refeicoes.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos_fornecedor.id"), nullable=True)
    ingrediente = Column(String, nullable=False)
    quantidade_estimada = Column(Integer, nullable=True)
    
    refeicao = relationship("RefeicaoORM", back_populates="itens")
    produto = relationship("ProdutoFornecedorORM")


# TABELAS PARA APROVISIONAMENTO (REQUISITO 4)

class ReservaRefeicaoORM(Base):
    __tablename__ = "reservas_refeicoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    utilizador_id = Column(Integer, ForeignKey("utilizadores.id"), nullable=False)
    refeicao_id = Column(Integer, ForeignKey("refeicoes.id"), nullable=False)
    data_reserva = Column(DateTime, default=datetime.utcnow, nullable=False)
    quantidade_pessoas = Column(Integer, default=1, nullable=False)
    
    refeicao = relationship("RefeicaoORM")
    utilizador = relationship("UserORM")


class PlanoProducaoORM(Base):
    __tablename__ = "plano_producao"
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    produto_nome = Column(String, nullable=False)
    quantidade_prevista = Column(Integer, nullable=False)
    quantidade_realizada = Column(Integer, nullable=False)
    desvio_percentual = Column(Float, nullable=False)
    requer_alerta = Column(Boolean, default=False, nullable=False)


class PedidoFornecedorORM(Base):
    __tablename__ = "pedidos_fornecedores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos_fornecedor.id"), nullable=False)
    quantidade_solicitada = Column(Integer, nullable=False)
    data_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_entrega_prevista = Column(Date, nullable=False)
    status = Column(String, default="pendente", nullable=False)
    ordem_prioridade = Column(Integer, nullable=False)
    
    fornecedor = relationship("FornecedorORM")
    produto = relationship("ProdutoFornecedorORM")


class HistoricoRefeicoesDiaORM(Base):
    """
    Histórico de TOTAL de refeições oferecidas por dia da semana e tipo.
    Ex: "Segunda almoço: 200 refeições", "Sexta jantar: 180 refeições"
    """
    __tablename__ = "historico_refeicoes_dia"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dia_semana = Column(String, nullable=False)  # "segunda", "terca", etc.
    tipo_refeicao = Column(String, nullable=False)  # "almoço" ou "jantar"
    total_refeicoes = Column(Integer, nullable=False)  # Total oferecido neste dia/tipo
    ultima_atualizacao = Column(DateTime, default=datetime.utcnow, nullable=False)


class HistoricoReservasPratoORM(Base):
    """
    Histórico de reservas por PRATO ESPECÍFICO em cada dia da semana e tipo.
    Ex: "Segunda almoço - Frango: 95 reservas de 200 totais = 47.5%"
    Usado para calcular a % de produção de cada prato.
    """
    __tablename__ = "historico_reservas_prato"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dia_semana = Column(String, nullable=False)  # "segunda", "terca", etc.
    tipo_refeicao = Column(String, nullable=False)  # "almoço" ou "jantar"
    descricao_prato = Column(String, nullable=False)  # Ex: "Frango grelhado", "Peixe assado"
    total_reservas = Column(Integer, nullable=False)  # Quantas vezes foi escolhido
    percentual_escolha = Column(Float, nullable=False)  # % em relação ao total do dia (0.0 a 1.0)
    ultima_atualizacao = Column(DateTime, default=datetime.utcnow, nullable=False)
