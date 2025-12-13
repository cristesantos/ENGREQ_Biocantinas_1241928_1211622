from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from biocantinas.backend.app.db.session import get_db
from biocantinas.backend.app.services.kpiService import KPIService
from biocantinas.backend.app.dtos.kpiDTO import (
    RefeicaoKPIDTO, DiaKPIDTO, EmentaKPIDTO,
    DesperdícioRefeicaoDTO, DesperdícioDiaDTO, DesperdícioEmentaDTO, KPIConsolidadoDTO
)
from datetime import date

router = APIRouter(prefix="/kpi", tags=["KPI"])

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
def get_kpi_ementa(ementa_id: int, db: Session = Depends(get_db)):
    """
    Calcula a percentagem média de produtos biológicos para uma ementa completa
    """
    try:
        kpi = KPIService.calcular_kpi_ementa(db, ementa_id)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPI: {str(e)}")

# ==== ENDPOINTS DE DESPERDÍCIO ====

@router.get("/desperdicio/refeicao/{refeicao_id}", response_model=DesperdícioRefeicaoDTO)
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

@router.get("/desperdicio/dia/{ementa_id}/{dia_semana}", response_model=DesperdícioDiaDTO)
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

@router.get("/desperdicio/ementa/{ementa_id}", response_model=DesperdícioEmentaDTO)
def get_desperdicio_ementa(ementa_id: int, db: Session = Depends(get_db)):
    """
    Calcula desperdício agregado de uma ementa completa
    """
    try:
        kpi = KPIService.calcular_desperdicio_ementa(db, ementa_id)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular desperdício: {str(e)}")

# ==== ENDPOINTS CONSOLIDADOS ====

@router.get("/consolidado/{ementa_id}", response_model=KPIConsolidadoDTO)
def get_kpi_consolidado(ementa_id: int, db: Session = Depends(get_db)):
    """
    Retorna KPI consolidado: percentagem biológica + taxa de desperdício + resumo de quantidades
    """
    try:
        kpi = KPIService.calcular_kpi_consolidado(db, ementa_id)
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPI consolidado: {str(e)}")
