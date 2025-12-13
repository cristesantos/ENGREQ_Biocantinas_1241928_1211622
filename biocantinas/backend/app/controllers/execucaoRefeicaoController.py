from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from typing import List
from ..dtos.execucaoRefeicaoDTO import ExecucaoRefeicao, ExecucaoRefeicaoCreate
from ..services.execucaoRefeicaoService import get_execucaoRefeicao_service
from ..auth.jwt import get_current_user, require_role
from ..dtos.userDTO import User

router = APIRouter(tags=["execucaoRefeicao"], prefix="/execucaoRefeicao")


@router.post("/", response_model=ExecucaoRefeicao)
def criar_execucao(execucao: ExecucaoRefeicaoCreate, user: User = Depends(require_role("DIETISTA"))):
    svc = get_execucaoRefeicao_service()
    return svc.criar_execucao(execucao)


@router.get("/", response_model=List[ExecucaoRefeicao])
def listar_execucoes(
    data_inicio: date,
    data_fim: date,
    user: User = Depends(get_current_user)
):
    svc = get_execucaoRefeicao_service()
    return svc.listar_por_periodo(data_inicio, data_fim)


@router.delete("/{execucao_id}")
def deletar_execucao(execucao_id: int, user: User = Depends(require_role("DIETISTA"))):
    svc = get_execucaoRefeicao_service()
    sucesso = svc.deletar_execucao(execucao_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return {"message": "Execução removida com sucesso"}
