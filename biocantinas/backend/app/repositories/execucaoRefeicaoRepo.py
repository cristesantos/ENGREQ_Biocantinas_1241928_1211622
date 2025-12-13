from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from ..db.models import ExecucaoRefeicaoORM
from ..models.execucaoRefeicao import ExecucaoRefeicaoModel


class ExecucaoRefeicaoRepo:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, model: ExecucaoRefeicaoModel) -> ExecucaoRefeicaoModel:
        orm = ExecucaoRefeicaoORM(
            refeicao_id=model.refeicao_id,
            data_execucao=model.data_execucao,
            quantidade_produzida=model.quantidade_produzida,
            quantidade_servida=model.quantidade_servida,
            quantidade_nao_servida=model.quantidade_nao_servida,
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        model.id = orm.id
        return model

    def listar_por_periodo(self, data_inicio: date, data_fim: date) -> List[ExecucaoRefeicaoModel]:
        results = (
            self.session.query(ExecucaoRefeicaoORM)
            .filter(ExecucaoRefeicaoORM.data_execucao >= data_inicio)
            .filter(ExecucaoRefeicaoORM.data_execucao <= data_fim)
            .all()
        )
        return [self._to_model(r) for r in results]

    def obter(self, execucao_id: int) -> Optional[ExecucaoRefeicaoModel]:
        orm = self.session.get(ExecucaoRefeicaoORM, execucao_id)
        return self._to_model(orm) if orm else None

    def deletar(self, execucao_id: int) -> bool:
        orm = self.session.get(ExecucaoRefeicaoORM, execucao_id)
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True

    def _to_model(self, orm: ExecucaoRefeicaoORM) -> ExecucaoRefeicaoModel:
        return ExecucaoRefeicaoModel(
            id=orm.id,
            refeicao_id=orm.refeicao_id,
            data_execucao=orm.data_execucao,
            quantidade_produzida=orm.quantidade_produzida,
            quantidade_servida=orm.quantidade_servida,
            quantidade_nao_servida=orm.quantidade_nao_servida,
        )
