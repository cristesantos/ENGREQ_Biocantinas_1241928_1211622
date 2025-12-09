from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from ..db.models import PedidoFornecedorORM, FornecedorORM, ProdutoFornecedorORM

class PedidoRepo:
    def __init__(self, session: Session):
        self.session = session
    
    def criar_pedido(self, produto_id: int, quantidade: int, data_entrega: date) -> PedidoFornecedorORM:
        """
        Cria pedido ao fornecedor com ordem baseada em data_inscricao.
        Fornecedor mais antigo tem prioridade.
        """
        # Buscar fornecedor do produto (aprovado e mais antigo)
        produto = self.session.get(ProdutoFornecedorORM, produto_id)
        if not produto:
            raise ValueError(f"Produto {produto_id} não encontrado")
        
        fornecedor = (
            self.session.query(FornecedorORM)
            .filter(FornecedorORM.id == produto.fornecedor_id)
            .filter(FornecedorORM.aprovado == True)
            .first()
        )
        
        if not fornecedor:
            raise ValueError(f"Nenhum fornecedor aprovado para o produto {produto.nome}")
        
        # Calcular ordem de prioridade (baseado em data_inscricao)
        ordem = self._calcular_ordem_prioridade(fornecedor.id)
        
        pedido = PedidoFornecedorORM(
            fornecedor_id=fornecedor.id,
            produto_id=produto_id,
            quantidade_solicitada=quantidade,
            data_entrega_prevista=data_entrega,
            ordem_prioridade=ordem,
            status="pendente"
        )
        
        self.session.add(pedido)
        self.session.commit()
        self.session.refresh(pedido)
        return pedido
    
    def _calcular_ordem_prioridade(self, fornecedor_id: int) -> int:
        """
        Calcula ordem de prioridade baseada na data de inscrição.
        Fornecedor mais antigo = prioridade 1
        """
        fornecedores_aprovados = (
            self.session.query(FornecedorORM)
            .filter(FornecedorORM.aprovado == True)
            .order_by(FornecedorORM.data_inscricao.asc())
            .all()
        )
        
        for idx, fornecedor in enumerate(fornecedores_aprovados, start=1):
            if fornecedor.id == fornecedor_id:
                return idx
        
        return 999  # Fallback
    
    def listar_todos(self) -> List[PedidoFornecedorORM]:
        return (
            self.session.query(PedidoFornecedorORM)
            .order_by(PedidoFornecedorORM.ordem_prioridade.asc())
            .all()
        )
    
    def listar_por_fornecedor(self, fornecedor_id: int) -> List[PedidoFornecedorORM]:
        return (
            self.session.query(PedidoFornecedorORM)
            .filter(PedidoFornecedorORM.fornecedor_id == fornecedor_id)
            .all()
        )
    
    def listar_por_status(self, status: str) -> List[PedidoFornecedorORM]:
        return (
            self.session.query(PedidoFornecedorORM)
            .filter(PedidoFornecedorORM.status == status)
            .all()
        )
    
    def obter(self, pedido_id: int) -> Optional[PedidoFornecedorORM]:
        return self.session.get(PedidoFornecedorORM, pedido_id)
    
    def atualizar_status(self, pedido_id: int, novo_status: str) -> Optional[PedidoFornecedorORM]:
        pedido = self.session.get(PedidoFornecedorORM, pedido_id)
        if not pedido:
            return None
        
        pedido.status = novo_status
        self.session.commit()
        self.session.refresh(pedido)
        return pedido
    
    def deletar(self, pedido_id: int) -> bool:
        pedido = self.session.get(PedidoFornecedorORM, pedido_id)
        if not pedido:
            return False
        
        self.session.delete(pedido)
        self.session.commit()
        return True
