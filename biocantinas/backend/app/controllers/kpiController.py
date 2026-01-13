from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..services.kpiService import KPIService
from ..dtos.kpiDTO import (
    RefeicaoKPIDTO, DiaKPIDTO, EmentaKPIDTO,
    DesperdicioRefeicaoDTO, DesperdicioDiaDTO, DesperdicioEmentaDTO, KPIConsolidadoDTO
)
from ..auth.jwt import get_current_user
from ..dtos.userDTO import User
from datetime import date
from ..db.models import EmentaORM

router = APIRouter(prefix="/kpi", tags=["KPI"])

def _validate_user_can_access_ementa(db: Session, user: User, ementa_id: int):
    """Valida se o user pode acessar a ementa baseado no seu role e atribuições."""
    if user.role == "ADMIN":
        return True
    
    ementa = db.query(EmentaORM).filter(EmentaORM.id == ementa_id).first()
    if not ementa:
        raise HTTPException(status_code=404, detail="Ementa não encontrada")
    
    if user.role == "GESTOR_CANTINA_CENTRAL":
        # Pode ver apenas ementas da cantina central
        if ementa.cantina_id and ementa.cantina.tipo != "CENTRAL":
            raise HTTPException(status_code=403, detail="Acesso negado: não é da cantina central")
        return True
    
    if user.role == "GESTOR_CANTINA":
        # Pode ver apenas ementas da sua cantina
        if not user.cantina_id or ementa.cantina_id != user.cantina_id:
            raise HTTPException(status_code=403, detail="Acesso negado: ementa não pertence à sua cantina")
        return True
    
    if user.role == "GESTOR_REFEITORIO":
        # Pode ver apenas ementas que têm refeições servidas no seu refeitório
        from ..db.models import RefeicaoORM, ExecucaoRefeicaoORM
        has_access = db.query(ExecucaoRefeicaoORM).join(
            RefeicaoORM, ExecucaoRefeicaoORM.refeicao_id == RefeicaoORM.id
        ).filter(
            RefeicaoORM.ementa_id == ementa_id,
            ExecucaoRefeicaoORM.refeitorio_id == user.refeitorio_id
        ).first()
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Acesso negado: ementa não servida no seu refeitório")
        return True
    
    raise HTTPException(status_code=403, detail="Role não autorizado")

# ==== ENDPOINTS DE BIOLÓGICO ====

@router.get("/refeicao/{refeicao_id}", response_model=RefeicaoKPIDTO)
def get_kpi_refeicao(refeicao_id: int, db: Session = Depends(get_db)):
    """
    Calcula a percentagem de produtos biológicos utilizados numa refeição específica
    """
    try:
        kpi = KPIService.calcular_kpi_refeicao(db, refeicao_id)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPI: {str(e)}")

@router.get("/dia/{ementa_id}/{dia_semana}", response_model=DiaKPIDTO)
def get_kpi_dia(ementa_id: int, dia_semana: int, db: Session = Depends(get_db)):
    """
    Calcula a percentagem de produtos biológicos para um dia inteiro (almoço + jantar)
    dia_semana: 1=Segunda, 2=Terça, 3=Quarta, 4=Quinta, 5=Sexta
    """
    if dia_semana < 1 or dia_semana > 5:
        raise HTTPException(status_code=400, detail="dia_semana deve estar entre 1 e 5")
    
    try:
        kpi = KPIService.calcular_kpi_dia(db, ementa_id, dia_semana)
        return kpi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPI: {str(e)}")

@router.get("/ementa/{ementa_id}", response_model=EmentaKPIDTO)
def get_kpi_ementa(ementa_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Calcula a percentagem média de produtos biológicos para uma ementa completa
    """
    _validate_user_can_access_ementa(db, user, ementa_id)
    try:
        kpi = KPIService.calcular_kpi_ementa(db, ementa_id)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPI: {str(e)}")

# ==== ENDPOINTS DE DESPERDÍCIO ====

@router.get("/desperdicio/refeicao/{refeicao_id}", response_model=DesperdicioRefeicaoDTO)
def get_desperdicio_refeicao(refeicao_id: int, data_execucao: date = None, db: Session = Depends(get_db)):
    """
    Calcula taxa de desperdício de uma refeição específica.
    Se data_execucao não for fornecida, usa a mais recente.
    """
    try:
        kpi = KPIService.calcular_desperdicio_refeicao(db, refeicao_id, data_execucao)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular desperdício: {str(e)}")

@router.get("/desperdicio/dia/{ementa_id}/{dia_semana}", response_model=DesperdicioDiaDTO)
def get_desperdicio_dia(ementa_id: int, dia_semana: int, db: Session = Depends(get_db)):
    """
    Calcula desperdício agregado de um dia (almoço + jantar)
    dia_semana: 1=Segunda, 2=Terça, 3=Quarta, 4=Quinta, 5=Sexta
    """
    if dia_semana < 1 or dia_semana > 5:
        raise HTTPException(status_code=400, detail="dia_semana deve estar entre 1 e 5")
    
    try:
        kpi = KPIService.calcular_desperdicio_dia(db, ementa_id, dia_semana)
        return kpi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular desperdício: {str(e)}")

@router.get("/desperdicio/ementa/{ementa_id}", response_model=DesperdicioEmentaDTO)
def get_desperdicio_ementa(ementa_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Calcula desperdício agregado de uma ementa completa
    """
    _validate_user_can_access_ementa(db, user, ementa_id)
    try:
        kpi = KPIService.calcular_desperdicio_ementa(db, ementa_id)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular desperdício: {str(e)}")

# ==== ENDPOINTS CONSOLIDADOS ====

@router.get("/consolidado/{ementa_id}", response_model=KPIConsolidadoDTO)
def get_kpi_consolidado(ementa_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Retorna KPI consolidado: percentagem biológica + taxa de desperdício + resumo de quantidades
    """
    _validate_user_can_access_ementa(db, user, ementa_id)
    try:
        kpi = KPIService.calcular_kpi_consolidado(db, ementa_id)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPI consolidado: {str(e)}")
