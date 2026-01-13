from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class FornecedorORM(Base):
    __tablename__ = "fornecedores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    data_inscricao = Column(Date, nullable=False)
    aprovado = Column(Boolean, default=False, nullable=False)
    local = Column(Boolean, default=False, nullable=False)
    certificado = Column(Boolean, default=False, nullable=False)
    usuario_id = Column(Integer, ForeignKey("utilizadores.id"), nullable=True)  # Vínculo com o usuário

    produtos = relationship("ProdutoFornecedorORM", back_populates="fornecedor", cascade="all, delete-orphan")
    usuario = relationship("UserORM", foreign_keys=[usuario_id])


class FornecedorEstadoORM(Base):
    """Estado sanitário e localização básica do fornecedor."""
    __tablename__ = "fornecedores_estado"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), unique=True, nullable=False)
    em_quarentena = Column(Boolean, default=False, nullable=False)
    freguesia = Column(String, nullable=True)

    fornecedor = relationship("FornecedorORM")


class FreguesiaFechoORM(Base):
    """Regista fechos sanitários por freguesia."""
    __tablename__ = "freguesias_fecho"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    __table_args__ = (UniqueConstraint("nome", name="uq_freguesia_nome"),)

class ProdutoFornecedorORM(Base):
    """Produto de um fornecedor específico (referencia o catálogo global)"""
    __tablename__ = "produtos_fornecedor"
    __table_args__ = (
        UniqueConstraint('fornecedor_id', 'produto_id', name='uq_fornecedor_produto'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos_catalogo.id"), nullable=False)
    data_inscricao = Column(DateTime, default=datetime.utcnow, nullable=False)
    preco_unitario = Column(Float, nullable=True)
    capacidade = Column(Integer, nullable=False)
    unidade_medida = Column(String, nullable=True)
    semana_producao_inicio = Column(Integer, nullable=False)  # Semana do ano (1-52)
    semana_producao_fim = Column(Integer, nullable=False)  # Semana do ano (1-52)
    biologico = Column(Boolean, default=True, nullable=False)
    certificado = Column(String, nullable=True)

    fornecedor = relationship("FornecedorORM", back_populates="produtos")
    produto = relationship("ProdutoORM", back_populates="fornecedores")


class ProdutoORM(Base):
    """Catálogo global de produtos"""
    __tablename__ = "produtos_catalogo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    tipo = Column(String, nullable=True)  # fruta, hortícola, proteína, etc.
    descricao = Column(Text, nullable=True)
    unidade_medida = Column(String, nullable=True)  # kg, unidade, litro, etc.
    epoca_tipica = Column(String, nullable=True)  # Outono, Inverno, Primavera, Verão
    ativo = Column(Boolean, default=True, nullable=False)

    # Relação com produtos de fornecedores
    fornecedores = relationship("ProdutoFornecedorORM", back_populates="produto", cascade="all, delete-orphan")

class UserORM(Base):
    __tablename__ = "utilizadores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    cantina_id = Column(Integer, ForeignKey("cantinas.id"), nullable=True)
    refeitorio_id = Column(Integer, ForeignKey("refeitorios.id"), nullable=True)
    
    cantina = relationship("CantinaORM", foreign_keys=[cantina_id], viewonly=True)
    refeitorio = relationship("RefeitorioORM", foreign_keys=[refeitorio_id], viewonly=True)


class CantinaORM(Base):
    """Unidade de cantina, podendo ser central ou local."""
    __tablename__ = "cantinas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    localizacao = Column(String, nullable=True)
    tipo = Column(String, default="CENTRAL", nullable=False)  # CENTRAL ou LOCAL
    gestor_id = Column(Integer, ForeignKey("utilizadores.id"), nullable=True)

    refeitorios = relationship("RefeitorioORM", back_populates="cantina", cascade="all, delete-orphan")
    ementas = relationship("EmentaORM", back_populates="cantina")


class RefeitorioORM(Base):
    """Refeitório pertencente a uma cantina, com gestor próprio."""
    __tablename__ = "refeitorios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    localizacao = Column(String, nullable=True)
    gestor_id = Column(Integer, ForeignKey("utilizadores.id"), nullable=True)
    cantina_id = Column(Integer, ForeignKey("cantinas.id"), nullable=True)

    cantina = relationship("CantinaORM", back_populates="refeitorios")
    execucoes = relationship("ExecucaoRefeicaoORM", back_populates="refeitorio")





class ReceitaORM(Base):
    """Catálogo de receitas fixas com ingredientes e quantidades definidas"""
    __tablename__ = "receitas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    tipo_refeicao = Column(String, nullable=True)  # "almoço", "jantar", "ambos"
    categoria = Column(String, nullable=True)  # "carne", "peixe", "vegetariano", etc.
    porcoes_base = Column(Integer, default=1, nullable=False)  # Número de porções para as quantidades definidas
    tempo_preparo = Column(Integer, nullable=True)  # Tempo de preparação em minutos
    ativa = Column(Boolean, default=True, nullable=False)
    
    ingredientes = relationship("ItemReceitaORM", back_populates="receita", cascade="all, delete-orphan")


class ItemReceitaORM(Base):
    """Ingredientes de uma receita com quantidades fixas"""
    __tablename__ = "itens_receita"
    id = Column(Integer, primary_key=True, autoincrement=True)
    receita_id = Column(Integer, ForeignKey("receitas.id"), nullable=False)
    produto_catalogo_id = Column(Integer, ForeignKey("produtos_catalogo.id"), nullable=False)
    quantidade_por_porcao = Column(Float, nullable=False)  # Quantidade em kg por porção
    
    receita = relationship("ReceitaORM", back_populates="ingredientes")
    produto = relationship("ProdutoORM")


class EmentaORM(Base):
    __tablename__ = "ementas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    cantina_id = Column(Integer, ForeignKey("cantinas.id"), nullable=True)
    
    refeicoes = relationship("RefeicaoORM", back_populates="ementa", cascade="all, delete-orphan")
    cantina = relationship("CantinaORM", back_populates="ementas")


class RefeicaoORM(Base):
    __tablename__ = "refeicoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ementa_id = Column(Integer, ForeignKey("ementas.id"), nullable=False)
    receita_id = Column(Integer, ForeignKey("receitas.id"), nullable=True)  # Referência à receita do catálogo
    dia_semana = Column(Integer, nullable=False)  # 1=Segunda, 2=Terça, ..., 5=Sexta
    tipo = Column(String, nullable=False)  # "almoço" ou "jantar"
    descricao = Column(Text, nullable=True)
    numero_porcoes = Column(Integer, nullable=True)  # Número de porções planejadas para esta refeição
    
    ementa = relationship("EmentaORM", back_populates="refeicoes")
    receita = relationship("ReceitaORM")
    itens = relationship("ItemRefeicaoORM", back_populates="refeicao", cascade="all, delete-orphan")
    execucoes = relationship("ExecucaoRefeicaoORM", back_populates="refeicao", cascade="all, delete-orphan")


class ItemRefeicaoORM(Base):
    __tablename__ = "itens_refeicao"
    id = Column(Integer, primary_key=True, autoincrement=True)
    refeicao_id = Column(Integer, ForeignKey("refeicoes.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos_fornecedor.id"), nullable=True)
    ingrediente = Column(String, nullable=False)
    quantidade_estimada = Column(Float, nullable=True)
    
    refeicao = relationship("RefeicaoORM", back_populates="itens")
    produto = relationship("ProdutoFornecedorORM")


class ExecucaoRefeicaoORM(Base):
    __tablename__ = "execucoes_refeicao"
    id = Column(Integer, primary_key=True, autoincrement=True)
    refeicao_id = Column(Integer, ForeignKey("refeicoes.id"), nullable=False)
    refeitorio_id = Column(Integer, ForeignKey("refeitorios.id"), nullable=True)
    data_execucao = Column(Date, nullable=False)
    quantidade_prevista = Column(Integer, nullable=True)  # Previsão do plano de produção
    quantidade_produzida = Column(Integer, nullable=False)  # O que foi efetivamente produzido
    quantidade_servida = Column(Integer, nullable=False)
    quantidade_nao_servida = Column(Integer, nullable=False)

    refeicao = relationship("RefeicaoORM", back_populates="execucoes")
    refeitorio = relationship("RefeitorioORM", back_populates="execucoes")

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
    periodo_data_inicio = Column(Date, nullable=False)  # Data início da semana/período
    periodo_data_fim = Column(Date, nullable=False)  # Data fim da semana/período
    data_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    produto_nome = Column(String, nullable=False)
    quantidade_prevista = Column(Integer, nullable=False)  # Planeado
    quantidade_realizada = Column(Integer, default=0, nullable=False)  # Executado/Consumido
    desvio_percentual = Column(Float, default=0.0, nullable=False)  # (realizada - prevista) / prevista * 100
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
