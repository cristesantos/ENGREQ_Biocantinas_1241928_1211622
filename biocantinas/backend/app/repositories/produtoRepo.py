from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import ProdutoFornecedorORM
from ..models.produto import ProdutoFornecedorModel

class ProdutoRepo:
    def __init__(self, session: Session):
        self.session = session
    
    def criar_produto(self, fornecedor_id: int, produto: ProdutoFornecedorModel) -> tuple[int, int, ProdutoFornecedorModel]:
        """Cria um produto para um fornecedor específico. Retorna (id, fornecedor_id, model)"""
        orm = ProdutoFornecedorORM(
            fornecedor_id=fornecedor_id,
            nome=produto.nome,
            tipo=produto.tipo,
            biologico=produto.biologico,
            intervalo_producao_inicio=produto.intervalo_producao_inicio,
            intervalo_producao_fim=produto.intervalo_producao_fim,
            capacidade=produto.capacidade,
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return (orm.id, orm.fornecedor_id, self._to_model(orm))
    
    def obter_produto(self, produto_id: int) -> Optional[tuple[int, int, ProdutoFornecedorModel]]:
        """Busca produto por ID e retorna (id, fornecedor_id, model)"""
        orm = self.session.get(ProdutoFornecedorORM, produto_id)
        if not orm:
            return None
        return (orm.id, orm.fornecedor_id, self._to_model(orm))
    
    def listar_todos(self) -> List[ProdutoFornecedorModel]:
        """Lista todos os produtos como Models"""
        orms = self.session.query(ProdutoFornecedorORM).all()
        return [self._to_model(orm) for orm in orms]
    
    def listar_por_fornecedor(self, fornecedor_id: int) -> List[ProdutoFornecedorModel]:
        """Lista produtos de um fornecedor específico"""
        orms = (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.fornecedor_id == fornecedor_id)
            .all()
        )
        return [self._to_model(orm) for orm in orms]
    
    def listar_por_tipo(self, tipo: str) -> List[ProdutoFornecedorModel]:
        """Lista produtos de um tipo específico (fruta, hortícola, etc)"""
        orms = (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.tipo == tipo)
            .all()
        )
        return [self._to_model(orm) for orm in orms]
    
    def listar_biologicos(self) -> List[ProdutoFornecedorModel]:
        """Lista apenas produtos biológicos"""
        orms = (
            self.session.query(ProdutoFornecedorORM)
            .filter(ProdutoFornecedorORM.biologico == True)
            .all()
        )
        return [self._to_model(orm) for orm in orms]
    
    def atualizar_produto(self, produto_id: int, produto: ProdutoFornecedorModel) -> Optional[ProdutoFornecedorModel]:
        """Atualiza um produto existente"""
        orm = self.session.get(ProdutoFornecedorORM, produto_id)
        if not orm:
            return None
        
        orm.nome = produto.nome
        orm.tipo = produto.tipo
        orm.biologico = produto.biologico
        orm.intervalo_producao_inicio = produto.intervalo_producao_inicio
        orm.intervalo_producao_fim = produto.intervalo_producao_fim
        orm.capacidade = produto.capacidade
        
        self.session.commit()
        self.session.refresh(orm)
        return self._to_model(orm)
    
    def deletar_produto(self, produto_id: int) -> bool:
        """Remove um produto"""
        orm = self.session.get(ProdutoFornecedorORM, produto_id)
        if not orm:
            return False
        
        self.session.delete(orm)
        self.session.commit()
        return True
    
    def _to_model(self, orm: ProdutoFornecedorORM) -> ProdutoFornecedorModel:
        """Converte ORM para Model"""
        return ProdutoFornecedorModel(
            nome=orm.nome,
            tipo=orm.tipo,
            biologico=orm.biologico,
            intervalo_producao_inicio=orm.intervalo_producao_inicio,
            intervalo_producao_fim=orm.intervalo_producao_fim,
            capacidade=orm.capacidade,
        )
