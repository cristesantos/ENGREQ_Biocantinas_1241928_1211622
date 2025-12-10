from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List
from sqlalchemy import func
from ..services.aprovisionamentoService import get_aprovisionamento_service
from ..auth.jwt import require_role, get_current_user
from ..dtos.userDTO import User
from ..dtos.aprovisionamentoDTO import ReservaRefeicaoCreate, ReservaRefeicaoDTO
from ..db.models import ReservaRefeicaoORM

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
    Usa PREVISÃO HISTÓRICA para estimar demanda baseada em padrões passados.
    
    Mostra:
    - Necessidades planejadas (baseado na ementa)
    - Necessidades previstas (usando histórico de popularidade por dia/prato)
    - Desvios percentuais
    
    LÓGICA:
    - Busca total de refeições do histórico por dia da semana
    - Aplica % de escolha de cada prato para calcular quantidades
    """
    service = get_aprovisionamento_service()
    
    necessidades_base = service.calcular_necessidades(data_inicio, data_fim)
    necessidades_previstas = service.ajustar_com_previsao_historica(
        necessidades_base.copy(), data_inicio, data_fim
    )
    
    # Calcular desvios para visualização
    desvios = {}
    for produto in set(necessidades_base.keys()) | set(necessidades_previstas.keys()):
        qtd_planejada = necessidades_base.get(produto, 0)
        qtd_prevista = necessidades_previstas.get(produto, 0)
        desvio = service.calcular_desvio(qtd_planejada, qtd_prevista)
        desvios[produto] = round(desvio, 2)
    
    # Buscar detalhes das ementas do período
    ementas = service.ementa_repo.listar_por_periodo(data_inicio, data_fim)
    refeicoes_detalhes = []
    from datetime import timedelta
    dias_semana_nomes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    dias_semana = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    
    historico_repo = service.historico_repo
    
    for ementa in ementas:
        # Iterar sobre cada dia da ementa que esteja no período selecionado
        data_atual = max(ementa.data_inicio, data_inicio)
        data_fim_ementa = min(ementa.data_fim, data_fim)
        
        while data_atual <= data_fim_ementa:
            dia_semana_num = data_atual.weekday() + 1  # 1=Segunda, 2=Terça, etc
            dia_semana_texto = dias_semana[data_atual.weekday()]
            
            # Buscar refeições deste dia da semana
            for refeicao in ementa.refeicoes:
                if refeicao.dia_semana == dia_semana_num:
                    ingredientes = [
                        {"ingrediente": item.ingrediente, "quantidade_estimada": item.quantidade_estimada}
                        for item in refeicao.itens
                    ]
                    
                    # Buscar previsão histórica
                    reservas_historico = historico_repo.obter_reservas_prato(
                        dia_semana_texto, refeicao.tipo.lower(), refeicao.descricao or ""
                    )
                    
                    # Contar reservas reais
                    reservas_reais = service.session.query(
                        func.sum(ReservaRefeicaoORM.quantidade_pessoas)
                    ).filter(
                        ReservaRefeicaoORM.refeicao_id == refeicao.id
                    ).scalar() or 0
                    
                    refeicoes_detalhes.append({
                        "data": str(data_atual),
                        "dia_nome": dias_semana_nomes[data_atual.weekday()],
                        "dia_semana_texto": dia_semana_texto.capitalize(),
                        "descricao": refeicao.descricao or f"Refeição {refeicao.tipo}",
                        "tipo": refeicao.tipo,
                        "ingredientes": ingredientes,
                        "previsao_reservas": reservas_historico,
                        "reservas_reais": int(reservas_reais)
                    })
            
            data_atual += timedelta(days=1)
    
    # Buscar detalhes do histórico para exibição
    historico_detalhes = []
    for ref in refeicoes_detalhes:
        historico_detalhes.append({
            "Data": ref["data"],
            "Dia": ref["dia_nome"],
            "Tipo": ref["tipo"].title(),
            "Prato": ref["descricao"],
            "Previsão Histórica": ref["previsao_reservas"],
            "Reservas Reais": ref["reservas_reais"]
        })
    
    return {
        "periodo": f"{data_inicio} a {data_fim}",
        "necessidades_planejadas": necessidades_base,
        "necessidades_previstas": necessidades_previstas,
        "necessidades_previstas_historico": necessidades_previstas,  # Alias para compatibilidade
        "desvios": desvios,
        "refeicoes_detalhes": refeicoes_detalhes,
        "historico_detalhes": historico_detalhes,
        "metodo": "previsao_historica"
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
