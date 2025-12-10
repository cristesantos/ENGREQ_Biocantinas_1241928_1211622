from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from ..db.models import HistoricoRefeicoesDiaORM, HistoricoReservasPratoORM


class HistoricoReservasRepo:
    """
    Repositório para dados históricos de refeições e reservas.
    Combina informações de 2 tabelas:
    - historico_refeicoes_dia: Total de refeições por dia/tipo
    - historico_reservas_prato: Distribuição de escolha por prato
    """
    def __init__(self, session: Session):
        self.session = session
    
    def obter_total_refeicoes(self, dia_semana: str, tipo_refeicao: str) -> Optional[int]:
        """
        Retorna o total de refeições oferecidas para um dia e tipo.
        Ex: obter_total_refeicoes("segunda", "almoço") -> 200
        """
        historico = self.session.query(HistoricoRefeicoesDiaORM).filter(
            HistoricoRefeicoesDiaORM.dia_semana == dia_semana.lower(),
            HistoricoRefeicoesDiaORM.tipo_refeicao == tipo_refeicao.lower()
        ).first()
        
        return historico.total_refeicoes if historico else None
    
    def obter_distribuicao_pratos(self, dia_semana: str, tipo_refeicao: str) -> List[Dict]:
        """
        Retorna a distribuição de pratos para um dia/tipo.
        Retorna: [{"prato": "Frango", "percentual": 0.475, "reservas": 95}, ...]
        """
        historicos = self.session.query(HistoricoReservasPratoORM).filter(
            HistoricoReservasPratoORM.dia_semana == dia_semana.lower(),
            HistoricoReservasPratoORM.tipo_refeicao == tipo_refeicao.lower()
        ).all()
        
        return [
            {
                "prato": h.descricao_prato,
                "percentual": h.percentual_escolha,
                "reservas": h.total_reservas
            }
            for h in historicos
        ]
    
    def obter_percentual_prato(self, dia_semana: str, tipo_refeicao: str, 
                               descricao_prato: str) -> Optional[float]:
        """
        Retorna o % de escolha de um prato específico em um dia/tipo.
        Ex: obter_percentual_prato("segunda", "almoço", "Frango") -> 0.475 (47.5%)
        """
        historico = self.session.query(HistoricoReservasPratoORM).filter(
            HistoricoReservasPratoORM.dia_semana == dia_semana.lower(),
            HistoricoReservasPratoORM.tipo_refeicao == tipo_refeicao.lower(),
            HistoricoReservasPratoORM.descricao_prato == descricao_prato
        ).first()
        
        return historico.percentual_escolha if historico else None
    
    def obter_reservas_prato(self, dia_semana: str, tipo_refeicao: str, 
                            descricao_prato: str) -> Optional[int]:
        """
        Retorna o número de reservas de um prato específico em um dia/tipo.
        Ex: obter_reservas_prato("segunda", "almoço", "Frango grelhado") -> 90
        """
        historico = self.session.query(HistoricoReservasPratoORM).filter(
            HistoricoReservasPratoORM.dia_semana == dia_semana.lower(),
            HistoricoReservasPratoORM.tipo_refeicao == tipo_refeicao.lower(),
            HistoricoReservasPratoORM.descricao_prato == descricao_prato
        ).first()
        
        return historico.total_reservas if historico else None
    
    def listar_todos_dias(self) -> List[HistoricoRefeicoesDiaORM]:
        """Retorna todos os registros de totais por dia."""
        return self.session.query(HistoricoRefeicoesDiaORM).all()
    
    def listar_todos_pratos(self) -> List[HistoricoReservasPratoORM]:
        """Retorna todos os registros de distribuição de pratos."""
        return self.session.query(HistoricoReservasPratoORM).order_by(
            HistoricoReservasPratoORM.dia_semana,
            HistoricoReservasPratoORM.tipo_refeicao,
            HistoricoReservasPratoORM.percentual_escolha.desc()
        ).all()
