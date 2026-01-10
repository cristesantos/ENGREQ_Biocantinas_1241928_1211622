from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import ProdutoORM
from ..models.produto import ProdutoModel
from ..mappings.mappers import produto_orm_to_model


class ProdutoCatalogoRepository:
    """Repositório para operações CRUD no catálogo global de produtos"""

    @staticmethod
    def get_all(session: Session, apenas_ativos: bool = True) -> List[ProdutoModel]:
        """Busca todos os produtos do catálogo"""
        query = session.query(ProdutoORM)
        if apenas_ativos:
            query = query.filter(ProdutoORM.ativo == True)
        produtos = query.all()
        return [produto_orm_to_model(p) for p in produtos]

    @staticmethod
    def get_by_id(session: Session, produto_id: int) -> Optional[ProdutoModel]:
        """Busca um produto por ID"""
        produto = session.query(ProdutoORM).filter(ProdutoORM.id == produto_id).first()
        return produto_orm_to_model(produto) if produto else None

    @staticmethod
    def get_by_nome(session: Session, nome: str) -> Optional[ProdutoModel]:
        """Busca um produto por nome exato"""
        produto = session.query(ProdutoORM).filter(ProdutoORM.nome == nome).first()
        return produto_orm_to_model(produto) if produto else None

    @staticmethod
    def search_by_nome(session: Session, nome: str) -> List[ProdutoModel]:
        """Busca produtos por nome parcial (LIKE)"""
        produtos = session.query(ProdutoORM).filter(ProdutoORM.nome.ilike(f"%{nome}%")).all()
        return [produto_orm_to_model(p) for p in produtos]

    @staticmethod
    def get_by_tipo(session: Session, tipo: str) -> List[ProdutoModel]:
        """Busca produtos por tipo"""
        produtos = session.query(ProdutoORM).filter(ProdutoORM.tipo == tipo).all()
        return [produto_orm_to_model(p) for p in produtos]

    @staticmethod
    def get_by_epoca(session: Session, epoca: str) -> List[ProdutoModel]:
        """Busca produtos por época típica"""
        produtos = session.query(ProdutoORM).filter(ProdutoORM.epoca_tipica == epoca).all()
        return [produto_orm_to_model(p) for p in produtos]

    @staticmethod
    def create(session: Session, produto: ProdutoModel) -> ProdutoModel:
        """Cria um novo produto no catálogo"""
        produto_orm = ProdutoORM(
            nome=produto.nome,
            tipo=produto.tipo,
            descricao=produto.descricao,
            unidade_medida=produto.unidade_medida,
            epoca_tipica=produto.epoca_tipica,
            ativo=produto.ativo
        )
        session.add(produto_orm)
        session.flush()
        return produto_orm_to_model(produto_orm)

    @staticmethod
    def update(session: Session, produto_id: int, produto_atualizado: ProdutoModel) -> Optional[ProdutoModel]:
        """Atualiza um produto existente"""
        produto_orm = session.query(ProdutoORM).filter(ProdutoORM.id == produto_id).first()
        if not produto_orm:
            return None

        if produto_atualizado.nome:
            produto_orm.nome = produto_atualizado.nome
        if produto_atualizado.tipo is not None:
            produto_orm.tipo = produto_atualizado.tipo
        if produto_atualizado.descricao is not None:
            produto_orm.descricao = produto_atualizado.descricao
        if produto_atualizado.unidade_medida is not None:
            produto_orm.unidade_medida = produto_atualizado.unidade_medida
        if produto_atualizado.epoca_tipica is not None:
            produto_orm.epoca_tipica = produto_atualizado.epoca_tipica
        produto_orm.ativo = produto_atualizado.ativo

        session.flush()
        return produto_orm_to_model(produto_orm)

    @staticmethod
    def delete(session: Session, produto_id: int) -> bool:
        """Remove um produto do catálogo (soft delete - marca como inativo)"""
        produto_orm = session.query(ProdutoORM).filter(ProdutoORM.id == produto_id).first()
        if not produto_orm:
            return False
        
        produto_orm.ativo = False
        session.flush()
        return True

    @staticmethod
    def hard_delete(session: Session, produto_id: int) -> bool:
        """Remove permanentemente um produto (apenas se não tiver fornecedores associados)"""
        produto_orm = session.query(ProdutoORM).filter(ProdutoORM.id == produto_id).first()
        if not produto_orm:
            return False
        
        session.delete(produto_orm)
        session.flush()
        return True
