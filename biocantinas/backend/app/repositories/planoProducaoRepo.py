from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import PlanoProducaoORM

class PlanoProducaoRepo:
    def __init__(self, session: Session):
        self.session = session
    
    def criar(self, dados: dict) -> PlanoProducaoORM:
        plano = PlanoProducaoORM(**dados)
        self.session.add(plano)
        self.session.commit()
        self.session.refresh(plano)
        return plano
    
    def listar_todos(self) -> List[PlanoProducaoORM]:
        return self.session.query(PlanoProducaoORM).all()
    
    def listar_alertas(self) -> List[PlanoProducaoORM]:
        """Lista apenas itens com desvio > 10% (requer_alerta = True)"""
        return (
            self.session.query(PlanoProducaoORM)
            .filter(PlanoProducaoORM.requer_alerta == True)
            .all()
        )
    
    def obter(self, plano_id: int) -> Optional[PlanoProducaoORM]:
        return self.session.get(PlanoProducaoORM, plano_id)
    
    def deletar(self, plano_id: int) -> bool:
        plano = self.session.get(PlanoProducaoORM, plano_id)
        if not plano:
            return False
        self.session.delete(plano)
        self.session.commit()
        return True
    
    def limpar_todos(self) -> int:
        """Remove todos os registros de plano de produção"""
        count = self.session.query(PlanoProducaoORM).count()
        self.session.query(PlanoProducaoORM).delete()
        self.session.commit()
        return count
