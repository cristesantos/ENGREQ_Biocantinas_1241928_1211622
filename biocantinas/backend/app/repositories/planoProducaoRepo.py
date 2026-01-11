from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from ..db.models import PlanoProducaoORM
from ..models.planoProducao import PlanoProducaoModel

class PlanoProducaoRepo:
    def __init__(self, session: Session):
        self.session = session
    
    def criar(self, dados: dict) -> PlanoProducaoModel:
        plano = PlanoProducaoORM(**dados)
        self.session.add(plano)
        self.session.commit()
        self.session.refresh(plano)
        return self._to_model(plano)
    
    def listar_todos(self) -> List[PlanoProducaoModel]:
        planos = self.session.query(PlanoProducaoORM).all()
        return [self._to_model(p) for p in planos]
    
    def listar_alertas(self) -> List[PlanoProducaoModel]:
        """Lista apenas itens com desvio > 10% (requer_alerta = True)"""
        planos = (
            self.session.query(PlanoProducaoORM)
            .filter(PlanoProducaoORM.requer_alerta == True)
            .all()
        )
        return [self._to_model(p) for p in planos]
    
    def obter(self, plano_id: int) -> Optional[PlanoProducaoModel]:
        plano = self.session.get(PlanoProducaoORM, plano_id)
        return self._to_model(plano) if plano else None
    
    def obter_por_periodo(self, data_inicio: date, data_fim: date) -> List[PlanoProducaoModel]:
        """Obtém todos os planos para um período"""
        planos = (
            self.session.query(PlanoProducaoORM)
            .filter(
                PlanoProducaoORM.periodo_data_inicio == data_inicio,
                PlanoProducaoORM.periodo_data_fim == data_fim,
            )
            .all()
        )
        return [self._to_model(p) for p in planos]
    
    def obter_por_produto_periodo(
        self, produto_nome: str, data_inicio: date, data_fim: date
    ) -> Optional[PlanoProducaoModel]:
        """Obtém plano para um produto específico em um período"""
        plano = (
            self.session.query(PlanoProducaoORM)
            .filter(
                PlanoProducaoORM.produto_nome == produto_nome,
                PlanoProducaoORM.periodo_data_inicio == data_inicio,
                PlanoProducaoORM.periodo_data_fim == data_fim,
            )
            .first()
        )
        return self._to_model(plano) if plano else None
    
    def atualizar(self, plano_id: int, dados: dict) -> Optional[PlanoProducaoModel]:
        """Atualiza um plano existente"""
        plano = self.session.get(PlanoProducaoORM, plano_id)
        if not plano:
            return None
        
        for key, value in dados.items():
            if hasattr(plano, key) and value is not None:
                setattr(plano, key, value)
        
        self.session.commit()
        self.session.refresh(plano)
        return self._to_model(plano)
    
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
    
    def _to_model(self, plano_orm: PlanoProducaoORM) -> PlanoProducaoModel:
        """Converte ORM para Model de domínio"""
        return PlanoProducaoModel(
            id=plano_orm.id,
            periodo_data_inicio=plano_orm.periodo_data_inicio,
            periodo_data_fim=plano_orm.periodo_data_fim,
            data_calculo=plano_orm.data_calculo,
            produto_nome=plano_orm.produto_nome,
            quantidade_prevista=plano_orm.quantidade_prevista,
            quantidade_realizada=plano_orm.quantidade_realizada,
            desvio_percentual=plano_orm.desvio_percentual,
            requer_alerta=plano_orm.requer_alerta,
        )
