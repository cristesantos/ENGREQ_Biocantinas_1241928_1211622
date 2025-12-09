from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List
from ..services.aprovisionamentoService import get_aprovisionamento_service
from ..auth.jwt import require_role, get_current_user
from ..dtos.userDTO import User
from ..dtos.aprovisionamentoDTO import ReservaRefeicaoCreate, ReservaRefeicaoDTO

router = APIRouter(prefix="/aprovisionamento", tags=["aprovisionamento"])

# ============ ENDPOINTS PARA RESERVAS DE REFEIÇÕES ============

@router.post("/reservas", response_model=ReservaRefeicaoDTO)
def criar_reserva(
    reserva: ReservaRefeicaoCreate,
    user: User = Depends(get_current_user)
):
    """Estudante reserva uma refeição específica"""
    service = get_aprovisionamento_service()
    try:
        reserva_criada = service.reserva_repo.criar(
            utilizador_id=user.id,
            refeicao_id=reserva.refeicao_id,
            quantidade_pessoas=reserva.quantidade_pessoas
        )
        return reserva_criada
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reservas", response_model=List[ReservaRefeicaoDTO])
def listar_minhas_reservas(user: User = Depends(get_current_user)):
    """Lista reservas do utilizador autenticado"""
    service = get_aprovisionamento_service()
    return service.reserva_repo.listar_por_utilizador(user.id)


# ============ ENDPOINTS PARA CÁLCULO DE NECESSIDADES ============

@router.get("/necessidades")
def calcular_necessidades(
    data_inicio: date,
    data_fim: date,
    user: User = Depends(get_current_user)
):
    """
    Calcula necessidades de produtos para um período baseado nas ementas planejadas.
    Endpoint público para visualização.
    """
    service = get_aprovisionamento_service()
    necessidades = service.calcular_necessidades(data_inicio, data_fim)
    
    return {
        "periodo": f"{data_inicio} a {data_fim}",
        "necessidades": necessidades,
        "total_produtos": len(necessidades)
    }


@router.get("/preview")
def preview_necessidades(
    data_inicio: date,
    data_fim: date,
    user: User = Depends(get_current_user)
):
    """
    Preview de necessidades SEM salvar no banco.
    Mostra:
    - Necessidades planejadas (baseado na ementa)
    - Necessidades ajustadas (com reservas)
    - Desvios percentuais
    """
    service = get_aprovisionamento_service()
    
    necessidades_base = service.calcular_necessidades(data_inicio, data_fim)
    necessidades_ajustadas, reservas = service.ajustar_com_reservas(
        necessidades_base.copy(), data_inicio, data_fim
    )
    
    # Calcular desvios para visualização
    desvios = {}
    for produto in set(necessidades_base.keys()) | set(necessidades_ajustadas.keys()):
        qtd_planejada = necessidades_base.get(produto, 0)
        qtd_ajustada = necessidades_ajustadas.get(produto, 0)
        desvio = service.calcular_desvio(qtd_planejada, qtd_ajustada)
        desvios[produto] = round(desvio, 2)
    
    return {
        "periodo": f"{data_inicio} a {data_fim}",
        "necessidades_planejadas": necessidades_base,
        "necessidades_com_reservas": necessidades_ajustadas,
        "desvios_percentuais": desvios
    }


# ============ ENDPOINTS EXCLUSIVOS DO GESTOR DA CANTINA ============

@router.post("/calcular-plano")
def calcular_plano_producao(
    data_inicio: date,
    data_fim: date,
    user: User = Depends(require_role("GESTOR_CANTINA"))
):
    """
    [GESTOR_CANTINA] Calcula e SALVA o plano de produção final.
    
    Processo:
    1. Calcula necessidades da ementa
    2. Ajusta com reservas reais
    3. Calcula desvios
    4. Gera alertas se desvio > 10%
    5. Salva tudo no banco de dados
    """
    service = get_aprovisionamento_service()
    resultado = service.calcular_e_salvar_plano(data_inicio, data_fim)
    
    return {
        "sucesso": True,
        "periodo": f"{data_inicio} a {data_fim}",
        **resultado
    }


@router.post("/gerar-pedidos")
def gerar_pedidos_fornecedores(
    data_inicio: date,
    data_fim: date,
    data_entrega: date,
    user: User = Depends(require_role("GESTOR_CANTINA"))
):
    """
    [GESTOR_CANTINA] Gera pedidos aos fornecedores aprovados.
    
    Ordem de prioridade baseada na data de inscrição:
    - Fornecedor mais antigo = prioridade 1
    - Segundo mais antigo = prioridade 2
    - etc.
    """
    service = get_aprovisionamento_service()
    resultado = service.gerar_pedidos_fornecedores(data_inicio, data_fim, data_entrega)
    
    return {
        "sucesso": True,
        "periodo": f"{data_inicio} a {data_fim}",
        "data_entrega": data_entrega,
        **resultado
    }


@router.get("/alertas")
def listar_alertas(user: User = Depends(require_role("GESTOR_CANTINA"))):
    """
    [GESTOR_CANTINA] Lista todos os alertas de desvio > 10%.
    """
    service = get_aprovisionamento_service()
    alertas = service.listar_alertas()
    
    return {
        "total_alertas": len(alertas),
        "alertas": alertas
    }


@router.get("/pedidos")
def listar_pedidos(
    status: str | None = None,
    user: User = Depends(require_role("GESTOR_CANTINA"))
):
    """
    [GESTOR_CANTINA] Lista pedidos aos fornecedores.
    Pode filtrar por status: pendente, confirmado, entregue
    """
    service = get_aprovisionamento_service()
    
    if status:
        pedidos = service.pedido_repo.listar_por_status(status)
    else:
        pedidos = service.pedido_repo.listar_todos()
    
    return {
        "total": len(pedidos),
        "pedidos": [
            {
                "id": p.id,
                "fornecedor": p.fornecedor.nome,
                "produto": p.produto.nome,
                "quantidade": p.quantidade_solicitada,
                "data_entrega_prevista": p.data_entrega_prevista,
                "status": p.status,
                "ordem_prioridade": p.ordem_prioridade
            }
            for p in pedidos
        ]
    }


@router.put("/pedidos/{pedido_id}/status")
def atualizar_status_pedido(
    pedido_id: int,
    novo_status: str,
    user: User = Depends(require_role("GESTOR_CANTINA"))
):
    """
    [GESTOR_CANTINA] Atualiza status de um pedido.
    Status válidos: pendente, confirmado, entregue
    """
    service = get_aprovisionamento_service()
    
    if novo_status not in ["pendente", "confirmado", "entregue"]:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    pedido = service.pedido_repo.atualizar_status(pedido_id, novo_status)
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return {
        "sucesso": True,
        "pedido_id": pedido.id,
        "novo_status": pedido.status
    }
