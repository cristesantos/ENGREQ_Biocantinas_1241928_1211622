from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import ProdutoFornecedorORM, ProdutoORM
from ..models.produto import ProdutoFornecedorModel
from ..mappings.mappers import produto_fornecedor_orm_to_model

class ProdutoFornecedorRepo:
    def __init__(self, session: Session):
        self.session = session
    
    def criar_produto(self, fornecedor_id: int, produto_id: int, capacidade: int, 
                     preco_unitario: Optional[float], unidade_medida: Optional[str],
                     intervalo_producao_inicio, intervalo_producao_fim, 
                     prioridade: int, biologico: bool, local: bool, disponivel: bool) -> ProdutoFornecedorModel:
        """Cria um produto para um fornecedor específico."""
        orm = ProdutoFornecedorORM(
            fornecedor_id=fornecedor_id,
            produto_id=produto_id,
            preco_unitario=preco_unitario,
            capacidade=capacidade,
            unidade_medida=unidade_medida,
            intervalo_producao_inicio=intervalo_producao_inicio,
            intervalo_producao_fim=intervalo_producao_fim,
            prioridade=prioridade,
            biologico=biologico,
            local=local,
            disponivel=disponivel
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return produto_fornecedor_orm_to_model(orm)
    
    def obter_produto(self, produto_fornecedor_id: int) -> Optional[ProdutoFornecedorModel]:
        """Busca produto de fornecedor por ID"""
        orm = self.session.query(ProdutoFornecedorORM).filter(
            ProdutoFornecedorORM.id == produto_fornecedor_id
        ).first()
        if not orm:
            return None
        return produto_fornecedor_orm_to_model(orm)
    
    def listar_todos(self) -> List[ProdutoFornecedorModel]:
        """Lista todos os produtos de fornecedores como Models"""
        orms = self.session.query(ProdutoFornecedorORM).all()
        return [produto_fornecedor_orm_to_model(orm) for orm in orms]
    
    def listar_por_fornecedor(self, fornecedor_id: int) -> List[ProdutoFornecedorModel]:
        """Lista produtos de um fornecedor específico"""
        orms = (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.fornecedor_id == fornecedor_id)
            .all()
        )
        return [produto_fornecedor_orm_to_model(orm) for orm in orms]
    
    def listar_por_tipo(self, tipo: str) -> List[ProdutoFornecedorModel]:
        """Lista produtos de fornecedores de um tipo específico (via produto do catálogo)"""
        orms = (
            self.session.query(ProdutoFornecedorORM)
            .join(ProdutoORM)
            .filter(ProdutoORM.tipo == tipo)
            .all()
        )
        return [produto_fornecedor_orm_to_model(orm) for orm in orms]
    
    def listar_biologicos(self) -> List[ProdutoFornecedorModel]:
        """Lista apenas produtos biológicos"""
        orms = (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.biologico == True)
            .all()
        )
        return [produto_fornecedor_orm_to_model(orm) for orm in orms]
    
    def listar_disponiveis(self, fornecedor_id: Optional[int] = None) -> List[ProdutoFornecedorModel]:
        """Lista produtos disponíveis, opcionalmente filtrados por fornecedor"""
        query = self.session.query(ProdutoFornecedorORM).filter(
            ProdutoFornecedorORM.disponivel == True
        )
        if fornecedor_id:
            query = query.filter(ProdutoFornecedorORM.fornecedor_id == fornecedor_id)
        orms = query.all()
        return [produto_fornecedor_orm_to_model(orm) for orm in orms]
    
    def atualizar_produto(self, produto_fornecedor_id: int, **kwargs) -> Optional[ProdutoFornecedorModel]:
        """Atualiza um produto de fornecedor existente"""
        orm = self.session.query(ProdutoFornecedorORM).filter(
            ProdutoFornecedorORM.id == produto_fornecedor_id
        ).first()
        if not orm:
            return None
        
        # Atualiza apenas campos fornecidos
        for key, value in kwargs.items():
            if hasattr(orm, key) and value is not None:
                setattr(orm, key, value)
        
        self.session.commit()
        self.session.refresh(orm)
        return produto_fornecedor_orm_to_model(orm)
    
    def deletar_produto(self, produto_fornecedor_id: int) -> bool:
        """Remove um produto de fornecedor"""
        orm = self.session.query(ProdutoFornecedorORM).filter(
            ProdutoFornecedorORM.id == produto_fornecedor_id
        ).first()
        if not orm:
            return False
        
        self.session.delete(orm)
        self.session.commit()
        return True

