"""
Controller para Receitas
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import date
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..dtos.receitaDTO import ReceitaDTO, ReceitaCreateDTO, ReceitaUpdateDTO
from ..services.receitaService import ReceitaService
from ..auth.jwt import get_current_user

router = APIRouter(prefix="/receitas", tags=["receitas"])


@router.post("/", response_model=ReceitaDTO, status_code=201)
def criar_receita(
    receita: ReceitaCreateDTO,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cria uma nova receita no catálogo"""
    # Apenas dietistas e admins podem criar receitas
    if current_user["role"] not in ["dietista", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        service = ReceitaService(session)
        return service.criar_receita(receita)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar receita: {str(e)}")


@router.get("/", response_model=List[ReceitaDTO])
def listar_receitas(
    apenas_ativas: bool = True,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista todas as receitas do catálogo"""
    try:
        service = ReceitaService(session)
        return service.listar_receitas(apenas_ativas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar receitas: {str(e)}")


@router.get("/disponiveis", response_model=List[ReceitaDTO])
def listar_receitas_disponiveis(
    semana: int,
    data: date | None = None,
    tipo: str | None = None,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista receitas viáveis para a semana, filtrando por disponibilidade de ingredientes.

    Args:
        semana: número da semana ISO (1-52)
        data: data opcional para validar o ano (para evitar receitas em anos sem produtos)
        tipo: opcional ("almoço" ou "jantar") para filtrar
    """
    if not (1 <= semana <= 52):
        raise HTTPException(status_code=400, detail="Semana deve estar entre 1 e 52")
    if tipo and tipo not in ["almoço", "jantar", "ambos"]:
        raise HTTPException(status_code=400, detail="Tipo deve ser 'almoço', 'jantar' ou 'ambos'")
    try:
        service = ReceitaService(session)
        return service.listar_receitas_disponiveis_semana(semana, tipo, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar receitas disponíveis: {str(e)}")


@router.get("/{receita_id}", response_model=ReceitaDTO)
def obter_receita(
    receita_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtém uma receita específica por ID"""
    try:
        service = ReceitaService(session)
        receita = service.obter_receita(receita_id)
        
        if not receita:
            raise HTTPException(status_code=404, detail="Receita não encontrada")
        
        return receita
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter receita: {str(e)}")


@router.put("/{receita_id}", response_model=ReceitaDTO)
def atualizar_receita(
    receita_id: int,
    receita: ReceitaUpdateDTO,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualiza uma receita existente"""
    # Apenas dietistas e admins podem atualizar receitas
    if current_user["role"] not in ["dietista", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        service = ReceitaService(session)
        receita_atualizada = service.atualizar_receita(receita_id, receita)
        
        if not receita_atualizada:
            raise HTTPException(status_code=404, detail="Receita não encontrada")
        
        return receita_atualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar receita: {str(e)}")


@router.delete("/{receita_id}", status_code=204)
def deletar_receita(
    receita_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deleta (desativa) uma receita"""
    # Apenas dietistas e admins podem deletar receitas
    if current_user["role"] not in ["dietista", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        service = ReceitaService(session)
        sucesso = service.deletar_receita(receita_id)
        
        if not sucesso:
            raise HTTPException(status_code=404, detail="Receita não encontrada")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar receita: {str(e)}")


@router.get("/categoria/{categoria}", response_model=List[ReceitaDTO])
def listar_receitas_por_categoria(
    categoria: str,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista receitas de uma categoria específica"""
    try:
        service = ReceitaService(session)
        return service.listar_receitas_por_categoria(categoria)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar receitas: {str(e)}")


@router.get("/tipo/{tipo_refeicao}", response_model=List[ReceitaDTO])
def listar_receitas_por_tipo(
    tipo_refeicao: str,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista receitas por tipo (almoço/jantar)"""
    if tipo_refeicao not in ["almoço", "jantar"]:
        raise HTTPException(status_code=400, detail="Tipo deve ser 'almoço' ou 'jantar'")
    
    try:
        service = ReceitaService(session)
        return service.listar_receitas_por_tipo(tipo_refeicao)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar receitas: {str(e)}")


@router.get("/{receita_id}/calcular/{num_porcoes}")
def calcular_necessidades(
    receita_id: int,
    num_porcoes: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Calcula as necessidades de ingredientes para N porções"""
    if num_porcoes <= 0:
        raise HTTPException(status_code=400, detail="Número de porções deve ser maior que zero")
    
    try:
        service = ReceitaService(session)
        resultado = service.calcular_necessidades_para_porcoes(receita_id, num_porcoes)
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Receita não encontrada")
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular necessidades: {str(e)}")
