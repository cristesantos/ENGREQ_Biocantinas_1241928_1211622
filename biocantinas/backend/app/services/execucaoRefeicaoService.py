from datetime import date
from typing import List
from ..db.session import SessionLocal, init_db
from ..repositories.execucaoRefeicaoRepo import ExecucaoRefeicaoRepo
from ..models.execucaoRefeicao import ExecucaoRefeicaoModel
from ..dtos.execucaoRefeicaoDTO import ExecucaoRefeicao, ExecucaoRefeicaoCreate


class ExecucaoRefeicaoService:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.repo = ExecucaoRefeicaoRepo(self.session)

    def criar_execucao(self, data: ExecucaoRefeicaoCreate) -> ExecucaoRefeicao:
        model = ExecucaoRefeicaoModel(
            id=0,
            refeicao_id=data.refeicao_id,
            data_execucao=data.data_execucao,
            quantidade_produzida=data.quantidade_produzida,
            quantidade_servida=data.quantidade_servida,
            quantidade_nao_servida=data.quantidade_nao_servida,
        )
        stored = self.repo.criar(model)
        return self._model_to_dto(stored)

    def listar_por_periodo(self, data_inicio: date, data_fim: date) -> List[ExecucaoRefeicao]:
        results = self.repo.listar_por_periodo(data_inicio, data_fim)
        return [self._model_to_dto(r) for r in results]

    def deletar_execucao(self, execucao_id: int) -> bool:
        return self.repo.deletar(execucao_id)

    def _model_to_dto(self, model: ExecucaoRefeicaoModel) -> ExecucaoRefeicao:
        return ExecucaoRefeicao(
            id=model.id,
            refeicao_id=model.refeicao_id,
            data_execucao=model.data_execucao,
            quantidade_produzida=model.quantidade_produzida,
            quantidade_servida=model.quantidade_servida,
            quantidade_nao_servida=model.quantidade_nao_servida,
        )


_service = ExecucaoRefeicaoService()

def get_execucaoRefeicao_service() -> ExecucaoRefeicaoService:
    return _service
