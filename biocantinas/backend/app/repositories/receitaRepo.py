"""
Repository para Receitas
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from ..db.models import ReceitaORM, ItemReceitaORM, ProdutoORM
from ..models.receita import ReceitaModel, ItemReceitaModel


class ReceitaRepository:
    """Repository para operações CRUD de receitas"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def criar_receita(self, receita: ReceitaModel) -> ReceitaModel:
        """Cria uma nova receita no banco de dados"""
        receita_orm = ReceitaORM(
            nome=receita.nome,
            descricao=receita.descricao,
            tipo_refeicao=receita.tipo_refeicao,
            categoria=receita.categoria,
            porcoes_base=receita.porcoes_base,
            tempo_preparo=receita.tempo_preparo,
            ativa=receita.ativa
        )
        
        # Adicionar ingredientes
        for ing in receita.ingredientes:
            item_orm = ItemReceitaORM(
                produto_catalogo_id=ing.produto_catalogo_id,
                quantidade_por_porcao=ing.quantidade_por_porcao
            )
            receita_orm.ingredientes.append(item_orm)
        
        self.session.add(receita_orm)
        self.session.commit()
        self.session.refresh(receita_orm)
        
        return self._orm_to_model(receita_orm)
    
    def listar_receitas(self, apenas_ativas: bool = True) -> List[ReceitaModel]:
        """Lista todas as receitas"""
        query = self.session.query(ReceitaORM).options(
            joinedload(ReceitaORM.ingredientes).joinedload(ItemReceitaORM.produto)
        )
        
        if apenas_ativas:
            query = query.filter(ReceitaORM.ativa == True)
        
        receitas_orm = query.all()
        return [self._orm_to_model(r) for r in receitas_orm]
    
    def obter_receita(self, receita_id: int) -> Optional[ReceitaModel]:
        """Obtém uma receita por ID"""
        receita_orm = self.session.query(ReceitaORM).options(
            joinedload(ReceitaORM.ingredientes).joinedload(ItemReceitaORM.produto)
        ).filter(ReceitaORM.id == receita_id).first()
        
        return self._orm_to_model(receita_orm) if receita_orm else None
    
    def obter_receita_por_nome(self, nome: str) -> Optional[ReceitaModel]:
        """Obtém uma receita por nome"""
        receita_orm = self.session.query(ReceitaORM).options(
            joinedload(ReceitaORM.ingredientes).joinedload(ItemReceitaORM.produto)
        ).filter(ReceitaORM.nome == nome).first()
        
        return self._orm_to_model(receita_orm) if receita_orm else None
    
    def atualizar_receita(self, receita_id: int, receita: ReceitaModel) -> Optional[ReceitaModel]:
        """Atualiza uma receita existente"""
        receita_orm = self.session.query(ReceitaORM).filter(ReceitaORM.id == receita_id).first()
        
        if not receita_orm:
            return None
        
        # Atualizar campos básicos
        if receita.nome:
            receita_orm.nome = receita.nome
        if receita.descricao is not None:
            receita_orm.descricao = receita.descricao
        if receita.tipo_refeicao:
            receita_orm.tipo_refeicao = receita.tipo_refeicao
        if receita.categoria:
            receita_orm.categoria = receita.categoria
        if receita.porcoes_base:
            receita_orm.porcoes_base = receita.porcoes_base
        if receita.tempo_preparo is not None:
            receita_orm.tempo_preparo = receita.tempo_preparo
        if receita.ativa is not None:
            receita_orm.ativa = receita.ativa
        
        # Atualizar ingredientes se fornecidos
        if receita.ingredientes:
            # Remover ingredientes antigos
            for item in receita_orm.ingredientes:
                self.session.delete(item)
            
            # Adicionar novos ingredientes
            for ing in receita.ingredientes:
                item_orm = ItemReceitaORM(
                    produto_catalogo_id=ing.produto_catalogo_id,
                    quantidade_por_porcao=ing.quantidade_por_porcao
                )
                receita_orm.ingredientes.append(item_orm)
        
        self.session.commit()
        self.session.refresh(receita_orm)
        
        return self._orm_to_model(receita_orm)
    
    def deletar_receita(self, receita_id: int) -> bool:
        """Deleta uma receita (soft delete)"""
        receita_orm = self.session.query(ReceitaORM).filter(ReceitaORM.id == receita_id).first()
        
        if not receita_orm:
            return False
        
        # Soft delete - marcar como inativa
        receita_orm.ativa = False
        self.session.commit()
        
        return True
    
    def listar_receitas_por_categoria(self, categoria: str) -> List[ReceitaModel]:
        """Lista receitas de uma categoria específica"""
        receitas_orm = self.session.query(ReceitaORM).options(
            joinedload(ReceitaORM.ingredientes).joinedload(ItemReceitaORM.produto)
        ).filter(
            ReceitaORM.categoria == categoria,
            ReceitaORM.ativa == True
        ).all()
        
        return [self._orm_to_model(r) for r in receitas_orm]
    
    def listar_receitas_por_tipo(self, tipo_refeicao: str) -> List[ReceitaModel]:
        """Lista receitas de um tipo específico (almoço/jantar)"""
        receitas_orm = self.session.query(ReceitaORM).options(
            joinedload(ReceitaORM.ingredientes).joinedload(ItemReceitaORM.produto)
        ).filter(
            ReceitaORM.tipo_refeicao.in_([tipo_refeicao, "ambos"]),
            ReceitaORM.ativa == True
        ).all()
        
        return [self._orm_to_model(r) for r in receitas_orm]
    
    def _orm_to_model(self, receita_orm: ReceitaORM) -> ReceitaModel:
        """Converte ReceitaORM para ReceitaModel"""
        ingredientes = [
            ItemReceitaModel(
                id=item.id,
                produto_catalogo_id=item.produto_catalogo_id,
                produto_nome=item.produto.nome if item.produto else "Desconhecido",
                quantidade_por_porcao=item.quantidade_por_porcao,
                unidade_medida=item.produto.unidade_medida if item.produto else None,
            )
            for item in receita_orm.ingredientes
        ]
        
        return ReceitaModel(
            id=receita_orm.id,
            nome=receita_orm.nome,
            descricao=receita_orm.descricao,
            tipo_refeicao=receita_orm.tipo_refeicao,
            categoria=receita_orm.categoria,
            porcoes_base=receita_orm.porcoes_base,
            tempo_preparo=receita_orm.tempo_preparo,
            ativa=receita_orm.ativa,
            ingredientes=ingredientes
        )
