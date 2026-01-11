from datetime import date
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db.models import (
    ExecucaoRefeicaoORM,
    RefeicaoORM,
    ItemRefeicaoORM,
    PlanoProducaoORM,
    ProdutoORM,
)
from ..db.session import SessionLocal, init_db


class RelatorioExecucaoService:
    """
    Serviço para calcular consumo real a partir de execuções de refeições
    e comparar com o plano de produção previsto.
    """

    def __init__(self):
        init_db()
        self.session = SessionLocal()

    def calcular_consumo_real(
        self, periodo_data_inicio: date, periodo_data_fim: date
    ) -> Dict[str, float]:
        """
        Calcula o consumo REAL de produtos baseado nas refeições que foram
        efetivamente produzidas e servidas no período.

        Lógica:
        1. Para cada execução no período
        2. Buscar a refeição e seus ingredientes
        3. Multiplicar quantidade_ingrediente × quantidade_produzida
        4. Somar por produto

        Retorna: {produto_nome: quantidade_consumida_total}
        """
        execucoes = self.session.query(ExecucaoRefeicaoORM).filter(
            ExecucaoRefeicaoORM.data_execucao >= periodo_data_inicio,
            ExecucaoRefeicaoORM.data_execucao <= periodo_data_fim,
        ).all()

        consumo = {}

        for execucao in execucoes:
            refeicao = self.session.query(RefeicaoORM).filter(
                RefeicaoORM.id == execucao.refeicao_id
            ).first()

            if not refeicao:
                continue

            # Iterar pelos ingredientes da refeição
            itens = self.session.query(ItemRefeicaoORM).filter(
                ItemRefeicaoORM.refeicao_id == refeicao.id
            ).all()
            
            for item in itens:
                produto_nome = item.ingrediente
                quantidade_ingrediente = item.quantidade_estimada or 0

                # Consumo = quantidade_ingrediente × quantidade_produzida
                consumo_item = quantidade_ingrediente * execucao.quantidade_produzida

                consumo[produto_nome] = consumo.get(produto_nome, 0) + consumo_item

        return consumo

    def gerar_relatorio_comparacao(
        self, periodo_data_inicio: date, periodo_data_fim: date
    ) -> Dict:
        """
        Gera relatório comparando:
        - Quantidade PREVISTA (do PlanoProducao)
        - Quantidade REALIZADA (calculada do consumo real)
        - Desvio

        Retorna estrutura com detalhes por produto
        """
        consumo_real = self.calcular_consumo_real(
            periodo_data_inicio, periodo_data_fim
        )

        # Buscar planos previsto do período
        planos = self.session.query(PlanoProducaoORM).filter(
            PlanoProducaoORM.periodo_data_inicio == periodo_data_inicio,
            PlanoProducaoORM.periodo_data_fim == periodo_data_fim,
        ).all()

        relatorio = {
            "periodo": {
                "data_inicio": str(periodo_data_inicio),
                "data_fim": str(periodo_data_fim),
            },
            "detalhes": [],
            "resumo": {
                "produtos_analisados": 0,
                "desvios_positivos": 0,  # Consumiu mais que o previsto
                "desvios_negativos": 0,  # Consumiu menos que o previsto
                "desvios_alerta": 0,  # Desvio > 10%
            },
        }

        todos_produtos = set()
        for plano in planos:
            todos_produtos.add(plano.produto_nome)
        for produto in consumo_real.keys():
            todos_produtos.add(produto)

        for produto_nome in sorted(todos_produtos):
            qty_prevista = next(
                (p.quantidade_prevista for p in planos if p.produto_nome == produto_nome),
                0,
            )
            qty_realizada = consumo_real.get(produto_nome, 0)

            if qty_prevista > 0:
                desvio_pct = ((qty_realizada - qty_prevista) / qty_prevista) * 100
            else:
                desvio_pct = 0.0 if qty_realizada == 0 else 100.0

            requer_alerta = abs(desvio_pct) > 10

            detalhe = {
                "produto": produto_nome,
                "quantidade_prevista": round(qty_prevista, 2),
                "quantidade_realizada": round(qty_realizada, 2),
                "desvio_percentual": round(desvio_pct, 2),
                "requer_alerta": requer_alerta,
                "status": (
                    "✅ OK"
                    if not requer_alerta
                    else (
                        "⬆️ Excesso" if desvio_pct > 0 else "⬇️ Falta"
                    )
                ),
            }

            relatorio["detalhes"].append(detalhe)

            relatorio["resumo"]["produtos_analisados"] += 1
            if desvio_pct > 0:
                relatorio["resumo"]["desvios_positivos"] += 1
            elif desvio_pct < 0:
                relatorio["resumo"]["desvios_negativos"] += 1
            if requer_alerta:
                relatorio["resumo"]["desvios_alerta"] += 1

        return relatorio

    def atualizar_plano_com_consumo_real(
        self, periodo_data_inicio: date, periodo_data_fim: date
    ) -> bool:
        """
        Atualiza a coluna quantidade_realizada dos PlanoProducao
        com os dados de consumo real calculados das execuções.

        Retorna True se teve sucesso
        """
        try:
            consumo_real = self.calcular_consumo_real(
                periodo_data_inicio, periodo_data_fim
            )

            # Atualizar planos do período
            planos = self.session.query(PlanoProducaoORM).filter(
                PlanoProducaoORM.periodo_data_inicio == periodo_data_inicio,
                PlanoProducaoORM.periodo_data_fim == periodo_data_fim,
            ).all()

            for plano in planos:
                qty_realizada = consumo_real.get(plano.produto_nome, 0)
                plano.quantidade_realizada = int(qty_realizada)

                if plano.quantidade_prevista > 0:
                    desvio = (
                        (qty_realizada - plano.quantidade_prevista)
                        / plano.quantidade_prevista
                        * 100
                    )
                else:
                    desvio = 0.0

                plano.desvio_percentual = round(desvio, 2)
                plano.requer_alerta = abs(desvio) > 10

            self.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar plano: {e}")
            self.session.rollback()
            return False
