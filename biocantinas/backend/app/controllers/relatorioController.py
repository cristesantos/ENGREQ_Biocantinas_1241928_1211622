from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.relatorioExecucaoService import RelatorioExecucaoService
from ..db.session import get_db
from ..auth.jwt import require_role

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/comparacao-execucao")
def get_comparacao_execucao(
    data_inicio: date,
    data_fim: date,
    session: Session = Depends(get_db),
    current_user: dict = Depends(require_role("GESTOR_CANTINA")),
):
    """
    Retorna comparação entre plano previsto e consumo realizado no período.

    Estrutura da resposta:
    {
        "periodo": {"data_inicio": "2026-01-01", "data_fim": "2026-01-07"},
        "detalhes": [
            {
                "produto": "Frango",
                "quantidade_prevista": 50,
                "quantidade_realizada": 52,
                "desvio_percentual": 4.0,
                "requer_alerta": false,
                "status": "✅ OK"
            },
            ...
        ],
        "resumo": {
            "produtos_analisados": 12,
            "desvios_positivos": 2,
            "desvios_negativos": 1,
            "desvios_alerta": 1
        }
    }
    """
    try:
        service = RelatorioExecucaoService()
        relatorio = service.gerar_relatorio_comparacao(data_inicio, data_fim)
        return relatorio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/atualizar-consumo-realizado")
def atualizar_consumo_realizado(
    data_inicio: date,
    data_fim: date,
    session: Session = Depends(get_db),
    current_user: dict = Depends(require_role("GESTOR_CANTINA")),
):
    """
    Calcula o consumo real das refeições executadas no período
    e atualiza os PlanoProducao com as quantidades realizadas.

    Retorna status da operação.
    """
    try:
        service = RelatorioExecucaoService()
        sucesso = service.atualizar_plano_com_consumo_real(data_inicio, data_fim)

        if sucesso:
            return {
                "sucesso": True,
                "mensagem": f"Plano de produção atualizado para {data_inicio} a {data_fim}",
            }
        else:
            raise HTTPException(
                status_code=500, detail="Erro ao atualizar plano de produção"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
