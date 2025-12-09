from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import ProdutoFornecedorORM

class ProdutoRepo:
    def __init__(self, session: Session):
        self.session = session
    
    def buscar_por_nome(self, nome: str) -> Optional[ProdutoFornecedorORM]:
        """Busca produto pelo nome exato"""
        return (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.nome == nome)
            .first()
        )
    
    def listar_todos(self) -> List[ProdutoFornecedorORM]:
        """Lista todos os produtos"""
        return self.session.query(ProdutoFornecedorORM).all()
    
    def listar_por_fornecedor(self, fornecedor_id: int) -> List[ProdutoFornecedorORM]:
        """Lista produtos de um fornecedor específico"""
        return (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.fornecedor_id == fornecedor_id)
            .all()
        )
    
    def listar_por_tipo(self, tipo: str) -> List[ProdutoFornecedorORM]:
        """Lista produtos de um tipo específico (fruta, hortícola, etc)"""
        return (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.tipo == tipo)
            .all()
        )
    
    def obter(self, produto_id: int) -> Optional[ProdutoFornecedorORM]:
        """Busca produto por ID"""
        return self.session.get(ProdutoFornecedorORM, produto_id)
