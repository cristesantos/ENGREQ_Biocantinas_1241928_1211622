from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import date
from ..dtos.ementaDTO import Ementa, EmentaCreate
from ..services.ementaService import get_ementa_service
from ..auth.jwt import get_current_user, require_role
from ..dtos.userDTO import User

router = APIRouter(tags=["ementas"], prefix="/ementas")


@router.post("/", response_model=Ementa)
def criar_ementa(ementa: EmentaCreate, user: User = Depends(require_role("DIETISTA"))):
    """Cria uma ementa manualmente"""
    svc = get_ementa_service()
    return svc.criar_ementa(ementa)


@router.post("/gerar", response_model=Ementa)
def gerar_ementa_automatica(
    data_inicio: date,
    nome: str | None = None,
    user: User = Depends(require_role("DIETISTA"))
):
    """Gera automaticamente uma ementa semanal baseada no stock disponível"""
    svc = get_ementa_service()
    try:
        return svc.gerar_ementa_automatica(data_inicio, nome)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ementa: {str(e)}")


@router.get("/", response_model=List[Ementa])
def listar_ementas(user: User = Depends(get_current_user)):
    """Lista todas as ementas"""
    svc = get_ementa_service()
    return svc.listar_ementas()


@router.get("/{ementa_id}", response_model=Ementa)
def obter_ementa(ementa_id: int, user: User = Depends(get_current_user)):
    """Obtém uma ementa específica com todas as refeições"""
    svc = get_ementa_service()
    ementa = svc.obter_ementa(ementa_id)
    if not ementa:
        raise HTTPException(status_code=404, detail="Ementa não encontrada")
    return ementa


@router.put("/{ementa_id}", response_model=Ementa)
def atualizar_ementa(
    ementa_id: int,
    ementa: EmentaCreate,
    user: User = Depends(require_role("DIETISTA"))
):
    """Atualiza uma ementa existente (nome, datas e refeições)."""
    svc = get_ementa_service()
    atualizado = svc.atualizar_ementa(ementa_id, ementa)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Ementa não encontrada")
    return atualizado


@router.delete("/{ementa_id}")
def deletar_ementa(ementa_id: int, user: User = Depends(require_role("DIETISTA"))):
    """Remove uma ementa"""
    svc = get_ementa_service()
    sucesso = svc.deletar_ementa(ementa_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Ementa não encontrada")
    return {"message": "Ementa removida com sucesso"}
