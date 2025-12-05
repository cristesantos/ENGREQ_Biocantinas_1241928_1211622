from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

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
    intervalo_producao_inicio = Column(Date, nullable=False)
    intervalo_producao_fim = Column(Date, nullable=False)
    capacidade = Column(Integer, nullable=False)

    fornecedor = relationship("FornecedorORM", back_populates="produtos")
