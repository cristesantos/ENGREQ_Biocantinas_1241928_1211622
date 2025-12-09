from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from ..db.models import ReservaRefeicaoORM, RefeicaoORM, EmentaORM

class ReservaRepo:
    def __init__(self, session: Session):
        self.session = session
    
    def criar(self, utilizador_id: int, refeicao_id: int, quantidade_pessoas: int = 1) -> ReservaRefeicaoORM:
        reserva = ReservaRefeicaoORM(
            utilizador_id=utilizador_id,
            refeicao_id=refeicao_id,
            quantidade_pessoas=quantidade_pessoas
        )
        self.session.add(reserva)
        self.session.commit()
        self.session.refresh(reserva)
        return reserva
    
    def listar_por_periodo(self, data_inicio: date, data_fim: date) -> List[ReservaRefeicaoORM]:
        """Lista reservas de refeições dentro do período da ementa"""
        return (
            self.session.query(ReservaRefeicaoORM)
            .join(ReservaRefeicaoORM.refeicao)
            .join(RefeicaoORM.ementa)
            .options(
                joinedload(ReservaRefeicaoORM.refeicao)
                .joinedload(RefeicaoORM.itens)
            )
            .filter(EmentaORM.data_inicio >= data_inicio)
            .filter(EmentaORM.data_fim <= data_fim)
            .all()
        )
    
    def listar_por_utilizador(self, utilizador_id: int) -> List[ReservaRefeicaoORM]:
        return (
            self.session.query(ReservaRefeicaoORM)
            .options(
                joinedload(ReservaRefeicaoORM.refeicao)
                .joinedload(RefeicaoORM.ementa)
            )
            .filter(ReservaRefeicaoORM.utilizador_id == utilizador_id)
            .all()
        )
    
    def listar_todas(self) -> List[ReservaRefeicaoORM]:
        return self.session.query(ReservaRefeicaoORM).all()
    
    def obter(self, reserva_id: int) -> Optional[ReservaRefeicaoORM]:
        return self.session.get(ReservaRefeicaoORM, reserva_id)
    
    def deletar(self, reserva_id: int) -> bool:
        reserva = self.session.get(ReservaRefeicaoORM, reserva_id)
        if not reserva:
            return False
        self.session.delete(reserva)
        self.session.commit()
        return True
