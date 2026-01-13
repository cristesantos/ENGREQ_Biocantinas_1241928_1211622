from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..db.session import get_db
from ..dtos.unidadeDTO import CantinaCreate, Cantina, RefeitorioCreate, Refeitorio
from ..repositories.cantinaRepo import CantinaRepo
from ..repositories.refeitorioRepo import RefeitorioRepo
from ..services.kpiService import KPIService
from ..schemas import User
from ..auth.jwt import require_role, require_any_role

router = APIRouter(prefix="/unidades", tags=["Unidades"])


@router.post("/cantinas", response_model=Cantina)
def criar_cantina(body: CantinaCreate, user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    repo = CantinaRepo(db)
    cantina = repo.criar(body.nome, body.localizacao, body.tipo, body.gestor_id)
    return cantina


@router.get("/cantinas", response_model=list[Cantina])
def listar_cantinas(user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA")), db: Session = Depends(get_db)):
    repo = CantinaRepo(db)
    return repo.listar()


@router.get("/cantinas/{cantina_id}", response_model=Cantina)
def obter_cantina(cantina_id: int, user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA")), db: Session = Depends(get_db)):
    repo = CantinaRepo(db)
    cantina = repo.obter(cantina_id)
    if not cantina:
        raise HTTPException(status_code=404, detail="Cantina não encontrada")
    return cantina


@router.patch("/cantinas/{cantina_id}", response_model=Cantina)
def atualizar_cantina(cantina_id: int, body: CantinaCreate, user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    repo = CantinaRepo(db)
    cantina = repo.atualizar(cantina_id, nome=body.nome, localizacao=body.localizacao, tipo=body.tipo, gestor_id=body.gestor_id)
    if not cantina:
        raise HTTPException(status_code=404, detail="Cantina não encontrada")
    return cantina


@router.delete("/cantinas/{cantina_id}")
def deletar_cantina(cantina_id: int, user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    repo = CantinaRepo(db)
    sucesso = repo.deletar(cantina_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Cantina não encontrada")
    return {"sucesso": True}


@router.post("/refeitorios", response_model=Refeitorio)
def criar_refeitorio(body: RefeitorioCreate, user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    repo = RefeitorioRepo(db)
    ref = repo.criar(body.nome, body.localizacao, body.gestor_id, body.cantina_id)
    return ref


@router.get("/refeitorios", response_model=list[Refeitorio])
def listar_refeitorios(user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA", "GESTOR_REFEITORIO")), db: Session = Depends(get_db)):
    repo = RefeitorioRepo(db)
    return repo.listar()


@router.get("/refeitorios/{refeitorio_id}", response_model=Refeitorio)
def obter_refeitorio(refeitorio_id: int, user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA", "GESTOR_REFEITORIO")), db: Session = Depends(get_db)):
    repo = RefeitorioRepo(db)
    ref = repo.obter(refeitorio_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Refeitório não encontrado")
    return ref


@router.patch("/refeitorios/{refeitorio_id}", response_model=Refeitorio)
def atualizar_refeitorio(refeitorio_id: int, body: RefeitorioCreate, user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    repo = RefeitorioRepo(db)
    ref = repo.atualizar(refeitorio_id, nome=body.nome, localizacao=body.localizacao, gestor_id=body.gestor_id, cantina_id=body.cantina_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Refeitório não encontrado")
    return ref


@router.delete("/refeitorios/{refeitorio_id}")
def deletar_refeitorio(refeitorio_id: int, user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    repo = RefeitorioRepo(db)
    sucesso = repo.deletar(refeitorio_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Refeitório não encontrado")
    return {"sucesso": True}


@router.get("/kpis/cantinas/{cantina_id}")
def kpis_cantina(
    cantina_id: int,
    data_inicio: date = Query(default_factory=lambda: (date.today() - timedelta(days=30))),
    data_fim: date = Query(default_factory=date.today),
    user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA")),
    db: Session = Depends(get_db)
):
    """
    Retorna KPIs de uma cantina no período especificado.
    - ADMIN: pode ver qualquer cantina
    - GESTOR_CANTINA_CENTRAL: pode ver a cantina central
    - GESTOR_CANTINA: pode ver sua própria cantina
    """
    kpi = KPIService.calcular_kpi_cantina(db, cantina_id, data_inicio, data_fim)
    return kpi


@router.get("/kpis/refeitorios/{refeitorio_id}")
def kpis_refeitorio(
    refeitorio_id: int,
    data_inicio: date = Query(default_factory=lambda: (date.today() - timedelta(days=30))),
    data_fim: date = Query(default_factory=date.today),
    user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA", "GESTOR_REFEITORIO")),
    db: Session = Depends(get_db)
):
    """
    Retorna KPIs de um refeitório no período especificado.
    - ADMIN: pode ver qualquer refeitório
    - GESTOR_CANTINA_CENTRAL: pode ver todos
    - GESTOR_CANTINA: pode ver refeitórios da sua cantina
    - GESTOR_REFEITORIO: pode ver seu próprio refeitório
    """
    kpi = KPIService.calcular_kpi_refeitorio(db, refeitorio_id, data_inicio, data_fim)
    return kpi


@router.get("/kpis/cantinas")
def kpis_todas_cantinas(
    data_inicio: date = Query(default_factory=lambda: (date.today() - timedelta(days=30))),
    data_fim: date = Query(default_factory=date.today),
    user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL")),
    db: Session = Depends(get_db)
):
    """
    Retorna KPIs de todas as cantinas no período.
    Disponível apenas para ADMIN e GESTOR_CANTINA_CENTRAL.
    """
    kpis = KPIService.calcular_kpi_todas_cantinas(db, data_inicio, data_fim)
    return {"total_cantinas": len(kpis), "periodo": {"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()}, "cantinas": kpis}


@router.get("/kpis/cantinas/{cantina_id}/refeitorios")
def kpis_refeitorios_da_cantina(
    cantina_id: int,
    data_inicio: date = Query(default_factory=lambda: (date.today() - timedelta(days=30))),
    data_fim: date = Query(default_factory=date.today),
    user: User = Depends(require_any_role("ADMIN", "GESTOR_CANTINA_CENTRAL", "GESTOR_CANTINA")),
    db: Session = Depends(get_db)
):
    """
    Retorna KPIs de todos os refeitórios de uma cantina no período.
    """
    kpis = KPIService.calcular_kpi_todos_refeitorios(db, cantina_id, data_inicio, data_fim)
    return {"cantina_id": cantina_id, "total_refeitorios": len(kpis), "periodo": {"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()}, "refeitorios": kpis}
