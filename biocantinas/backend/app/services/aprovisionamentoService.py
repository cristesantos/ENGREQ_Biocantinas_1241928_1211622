from datetime import date
from typing import Dict, List
from ..db.session import SessionLocal, init_db
from ..repositories.ementaRepo import EmentaRepo
from ..repositories.reservaRepo import ReservaRepo
from ..repositories.planoProducaoRepo import PlanoProducaoRepo
from ..repositories.pedidoRepo import PedidoRepo
from ..repositories.produtoRepo import ProdutoRepo
from ..repositories.historicoReservasRepo import HistoricoReservasRepo

class AprovisionamentoService:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.ementa_repo = EmentaRepo(self.session)
        self.reserva_repo = ReservaRepo(self.session)
        self.plano_repo = PlanoProducaoRepo(self.session)
        self.pedido_repo = PedidoRepo(self.session)
        self.produto_repo = ProdutoRepo(self.session)
        self.historico_repo = HistoricoReservasRepo(self.session)
    
    def calcular_necessidades(self, data_inicio: date, data_fim: date) -> Dict[str, int]:
        """
        ETAPA 1: Calcula quantidade de produtos necessários baseado na ementa planejada.
        
        Percorre: EMENTA → DIAS DO PERÍODO → REFEIÇÕES DO DIA → ITENS (ingredientes)
        
        IMPORTANTE: Calcula para cada DIA do período selecionado, somando a quantidade
        de ingredientes de cada refeição multiplicada pelo número de vezes que ela
        aparece no período.
        
        Retorna: {produto_nome: quantidade_total_kg}
        """
        from datetime import timedelta
        
        ementas = self.ementa_repo.listar_por_periodo(data_inicio, data_fim)
        necessidades = {}
        
        for ementa in ementas:
            # Iterar sobre cada dia do período selecionado
            data_atual = max(ementa.data_inicio, data_inicio)
            data_fim_ementa = min(ementa.data_fim, data_fim)
            
            while data_atual <= data_fim_ementa:
                dia_semana_num = data_atual.weekday() + 1  # 1=Segunda, 2=Terça, etc
                
                # Processar apenas as refeições deste dia da semana
                for refeicao in ementa.refeicoes:
                    if refeicao.dia_semana != dia_semana_num:
                        continue
                    
                    for item in refeicao.itens:
                        produto = item.ingrediente
                        quantidade = item.quantidade_estimada or 0
                        necessidades[produto] = necessidades.get(produto, 0) + quantidade
                
                data_atual += timedelta(days=1)
        
        return necessidades
    
    def ajustar_com_reservas(self, necessidades: Dict[str, int], 
                            data_inicio: date, data_fim: date) -> tuple[Dict[str, int], Dict[str, int]]:
        """
        ETAPA 2: Ajusta quantidades com base no histórico de reservas reais.
        
        - Se mais pessoas reservaram → aumenta quantidade
        - Se menos pessoas → mantém necessidade base
        
        Retorna: (necessidades_ajustadas, reservas_por_produto)
        """
        reservas = self.reserva_repo.listar_por_periodo(data_inicio, data_fim)
        necessidades_ajustadas = necessidades.copy()
        reservas_por_produto = {}
        
        # Agrupar reservas por produto
        for reserva in reservas:
            for item in reserva.refeicao.itens:
                produto = item.ingrediente
                # Assumir que receita é para 10 pessoas
                quantidade_por_pessoa = (item.quantidade_estimada or 0) / 10
                adicional = int(reserva.quantidade_pessoas * quantidade_por_pessoa)
                
                reservas_por_produto[produto] = reservas_por_produto.get(produto, 0) + adicional
                necessidades_ajustadas[produto] = necessidades_ajustadas.get(produto, 0) + adicional
        
        return necessidades_ajustadas, reservas_por_produto
    
    def ajustar_com_previsao_historica(self, necessidades: Dict[str, int], 
                                      data_inicio: date, data_fim: date) -> Dict[str, int]:
        """
        ETAPA 2 ALTERNATIVA: Ajusta quantidades usando histórico de refeições.
        
        LÓGICA IMPLEMENTADA:
        1. Para cada dia do período, identifica o dia da semana (ex: "segunda")
        2. Busca o TOTAL de refeições oferecidas naquele dia/tipo no histórico
        3. Para cada prato na ementa, busca o PERCENTUAL de escolha no histórico
        4. Calcula quantidade = (total_refeições_histórico × percentual_prato)
        
        EXEMPLO PRÁTICO:
        - Ementa de segunda tem "Frango grelhado" com 1kg de frango por porção
        - Histórico diz: Segunda almoço = 180 refeições totais
        - Histórico diz: "Frango grelhado" = 50% das escolhas na segunda
        - Cálculo: 180 refeições × 50% = 90 porções de frango
        - Quantidade ingrediente: 1kg × 90 = 90kg de frango
        
        Retorna: necessidades_ajustadas por produto
        """
        from datetime import timedelta
        
        ementas = self.ementa_repo.listar_por_periodo(data_inicio, data_fim)
        necessidades_ajustadas = {}
        
        # Mapa de dias da semana (0=segunda, 1=terça, ...)
        dias_semana_map = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
        
        for ementa in ementas:
            # Processar cada dia da ementa dentro do período selecionado
            data_atual = max(ementa.data_inicio, data_inicio)
            data_fim_ementa = min(ementa.data_fim, data_fim)
            
            while data_atual <= data_fim_ementa:
                dia_semana_nome = dias_semana_map[data_atual.weekday()]
                dia_semana_num = data_atual.weekday() + 1  # 1=Segunda, 2=Terça, etc
                
                # Processar apenas as refeições deste dia da semana
                for refeicao in ementa.refeicoes:
                    # Filtrar apenas refeições do dia da semana atual
                    if refeicao.dia_semana != dia_semana_num:
                        continue
                    tipo_refeicao = refeicao.tipo.lower()
                    descricao_prato = refeicao.descricao or ""
                    
                    # PASSO 1: Buscar número de reservas deste prato específico no histórico
                    # Ex: "Lasanha vegetariana" no almoço da quarta-feira teve 30 reservas
                    numero_reservas_historico = self.historico_repo.obter_reservas_prato(
                        dia_semana_nome, tipo_refeicao, descricao_prato
                    )
                    
                    if numero_reservas_historico is None:
                        # Sem histórico para este prato específico, usar quantidade base (1 porção)
                        for item in refeicao.itens:
                            produto = item.ingrediente
                            quantidade = item.quantidade_estimada or 0
                            necessidades_ajustadas[produto] = necessidades_ajustadas.get(produto, 0) + quantidade
                        continue
                    
                    # PASSO 2: Multiplicar quantidade de cada ingrediente pelo número de reservas
                    # Exemplo: Lasanha com 1kg curgete teve 30 reservas → 1kg × 30 = 30kg
                    for item in refeicao.itens:
                        produto = item.ingrediente
                        quantidade_por_reserva = item.quantidade_estimada or 0
                        
                        # Quantidade total = quantidade_por_reserva × número_de_reservas_histórico
                        # Exemplo: 1kg curgete × 30 reservas = 30kg de curgete
                        quantidade_total = quantidade_por_reserva * numero_reservas_historico
                        
                        necessidades_ajustadas[produto] = necessidades_ajustadas.get(produto, 0) + quantidade_total
                
                data_atual += timedelta(days=1)
        
        return necessidades_ajustadas
    
    def calcular_desvio(self, planejado: int, realizado: int) -> float:
        """Calcula desvio percentual entre planejado e realizado"""
        if planejado == 0:
            return 100.0 if realizado > 0 else 0.0
        
        return ((realizado - planejado) / planejado) * 100
    
    def gerar_alerta_desvio(self, desvio: float) -> bool:
        """Retorna True se desvio > 10%"""
        return abs(desvio) > 10
    
    def calcular_e_salvar_plano(self, data_inicio: date, data_fim: date) -> Dict:
        """
        ETAPA 3: Fluxo completo do aprovisionamento (PLANO FINAL COM RESERVAS REAIS)
        
        Este método é usado quando o GESTOR_CANTINA calcula o plano de produção final.
        Usa RESERVAS REAIS já feitas pelos estudantes, não previsão histórica.
        
        1. Calcula necessidades base (ementa planejada)
        2. Ajusta com RESERVAS REAIS de estudantes (não histórico)
        3. Calcula desvios percentuais
        4. Gera alertas se desvio > 10%
        5. Salva no plano de produção
        
        Retorna: {"plano": [...], "alertas": [...]}
        """
        # Limpar planos anteriores para este período
        self.plano_repo.limpar_todos()
        
        necessidades_base = self.calcular_necessidades(data_inicio, data_fim)
        
        # Usar RESERVAS REAIS (não previsão histórica)
        necessidades_ajustadas, reservas_por_produto = self.ajustar_com_reservas(
            necessidades_base, data_inicio, data_fim
        )
        
        # Combinar todos os produtos (planejados + reservados)
        todos_produtos = set(necessidades_base.keys()) | set(necessidades_ajustadas.keys())
        
        plano = []
        alertas = []
        
        for produto in todos_produtos:
            qtd_planejada = necessidades_base.get(produto, 0)
            qtd_real = necessidades_ajustadas.get(produto, 0)
            
            desvio = self.calcular_desvio(qtd_planejada, qtd_real)
            requer_alerta = self.gerar_alerta_desvio(desvio)
            
            plano_item = {
                "produto_nome": produto,
                "quantidade_prevista": qtd_planejada,
                "quantidade_realizada": qtd_real,
                "desvio_percentual": round(desvio, 2),
                "requer_alerta": requer_alerta
            }
            plano.append(plano_item)
            
            if requer_alerta:
                alertas.append({
                    "produto": produto,
                    "desvio": round(desvio, 2),
                    "mensagem": f"⚠️ Desvio de {desvio:.1f}% no produto '{produto}'"
                })
            
            # Salvar no banco de dados
            self.plano_repo.criar(plano_item)
        
        return {
            "plano": plano,
            "alertas": alertas,
            "total_produtos": len(plano),
            "produtos_com_alerta": len(alertas)
        }
    
    def gerar_pedidos_fornecedores(self, data_inicio: date, data_fim: date, data_entrega: date) -> List:
        """
        ETAPA 4: Gera pedidos aos fornecedores aprovados
        
        Ordem baseada na data de inscrição do fornecedor:
        - Fornecedor mais antigo = prioridade 1
        - Segundo mais antigo = prioridade 2
        - E assim por diante
        
        Retorna: lista de pedidos criados
        """
        necessidades = self.calcular_necessidades(data_inicio, data_fim)
        pedidos_criados = []
        erros = []
        
        for produto_nome, quantidade in necessidades.items():
            try:
                # Buscar produto no banco pelo nome
                produto = self.produto_repo.buscar_por_nome(produto_nome)
                
                if not produto:
                    erros.append(f"Produto '{produto_nome}' não encontrado no catálogo")
                    continue
                
                # Criar pedido (ordem automática por data_inscricao)
                pedido = self.pedido_repo.criar_pedido(
                    produto_id=produto.id,
                    quantidade=quantidade,
                    data_entrega=data_entrega
                )
                
                pedidos_criados.append({
                    "produto": produto_nome,
                    "quantidade": quantidade,
                    "fornecedor": pedido.fornecedor.nome,
                    "ordem_prioridade": pedido.ordem_prioridade,
                    "status": pedido.status
                })
                
            except ValueError as e:
                erros.append(str(e))
        
        return {
            "pedidos_criados": pedidos_criados,
            "total": len(pedidos_criados),
            "erros": erros
        }
    
    def listar_alertas(self) -> List:
        """Lista todos os alertas de desvio > 10%"""
        alertas_orm = self.plano_repo.listar_alertas()
        
        return [
            {
                "produto": alerta.produto_nome,
                "quantidade_prevista": alerta.quantidade_prevista,
                "quantidade_realizada": alerta.quantidade_realizada,
                "desvio_percentual": alerta.desvio_percentual,
                "data_calculo": alerta.data_calculo
            }
            for alerta in alertas_orm
        ]


# Singleton
_service = None

def get_aprovisionamento_service() -> AprovisionamentoService:
    global _service
    if _service is None:
        _service = AprovisionamentoService()
    return _service
