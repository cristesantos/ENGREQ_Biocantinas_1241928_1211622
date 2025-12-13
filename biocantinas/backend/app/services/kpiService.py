from sqlalchemy.orm import Session
from biocantinas.backend.app.db.models import (
    RefeicaoORM, ItemRefeicaoORM, EmentaORM, ProdutoFornecedorORM, ExecucaoRefeicaoORM
)
from biocantinas.backend.app.dtos.kpiDTO import (
    RefeicaoKPIDTO, IngredienteKPIDTO, DiaKPIDTO, EmentaKPIDTO,
    DesperdícioRefeicaoDTO, DesperdícioDiaDTO, DesperdícioEmentaDTO, KPIConsolidadoDTO
)
from typing import List
from statistics import mean
from datetime import date

class KPIService:
    
    @staticmethod
    def calcular_kpi_refeicao(session: Session, refeicao_id: int) -> RefeicaoKPIDTO:
        """
        Calcula a percentagem de produtos biológicos numa refeição
        """
        refeicao = session.query(RefeicaoORM).filter(RefeicaoORM.id == refeicao_id).first()
        
        if not refeicao:
            raise ValueError(f"Refeição com ID {refeicao_id} não encontrada")
        
        itens = session.query(ItemRefeicaoORM).filter(
            ItemRefeicaoORM.refeicao_id == refeicao_id
        ).all()
        
        if not itens:
            return RefeicaoKPIDTO(
                refeicao_id=refeicao_id,
                refeicao_descricao=refeicao.descricao or "",
                total_ingredientes=0,
                ingredientes_biologicos=0,
                percentagem_biologica=0.0,
                ingredientes=[]
            )
        
        ingredientes_kpi = []
        biologicos_count = 0
        
        for item in itens:
            # Tentar buscar o produto pelo produto_id se existir
            produto = None
            if item.produto_id:
                produto = session.query(ProdutoFornecedorORM).filter(
                    ProdutoFornecedorORM.id == item.produto_id
                ).first()
            
            # Se não tem produto_id, tentar buscar pelo nome (mais flexível)
            if not produto:
                produto = session.query(ProdutoFornecedorORM).filter(
                    ProdutoFornecedorORM.nome.ilike(f"%{item.ingrediente}%")
                ).first()
            
            is_biologico = produto.biologico if produto else False
            
            if is_biologico:
                biologicos_count += 1
            
            ingredientes_kpi.append(
                IngredienteKPIDTO(
                    nome=item.ingrediente,
                    biologico=is_biologico,
                    fornecedor_id=produto.fornecedor_id if produto else None
                )
            )

        total_ingredientes = len(itens)
        percentagem = (biologicos_count / total_ingredientes * 100) if total_ingredientes > 0 else 0.0
        
        return RefeicaoKPIDTO(
            refeicao_id=refeicao_id,
            refeicao_descricao=refeicao.descricao or "",
            total_ingredientes=total_ingredientes,
            ingredientes_biologicos=biologicos_count,
            percentagem_biologica=round(percentagem, 2),
            ingredientes=ingredientes_kpi
        )
    
    @staticmethod
    def calcular_kpi_dia(session: Session, ementa_id: int, dia_semana: int) -> DiaKPIDTO:
        """
        Calcula a percentagem de produtos biológicos para um dia inteiro (almoço + jantar)
        """
        refeicoes = session.query(RefeicaoORM).filter(
            RefeicaoORM.ementa_id == ementa_id,
            RefeicaoORM.dia_semana == dia_semana
        ).all()
        
        percentagens = []
        
        for refeicao in refeicoes:
            kpi = KPIService.calcular_kpi_refeicao(session, refeicao.id)
            percentagens.append(kpi.percentagem_biologica)
        
        media_percentagem = mean(percentagens) if percentagens else 0.0
        
        # Separar por tipo de refeição
        almoco = session.query(RefeicaoORM).filter(
            RefeicaoORM.ementa_id == ementa_id,
            RefeicaoORM.dia_semana == dia_semana,
            RefeicaoORM.tipo == "almoço"
        ).first()
        
        jantar = session.query(RefeicaoORM).filter(
            RefeicaoORM.ementa_id == ementa_id,
            RefeicaoORM.dia_semana == dia_semana,
            RefeicaoORM.tipo == "jantar"
        ).first()
        
        perc_almoco = KPIService.calcular_kpi_refeicao(session, almoco.id).percentagem_biologica if almoco else 0.0
        perc_jantar = KPIService.calcular_kpi_refeicao(session, jantar.id).percentagem_biologica if jantar else 0.0
        
        return DiaKPIDTO(
            ementa_id=ementa_id,
            dia_semana=dia_semana,
            percentagem_biologica_almoco=perc_almoco,
            percentagem_biologica_jantar=perc_jantar,
            media_percentagem_biologica=round(media_percentagem, 2)
        )
    
    @staticmethod
    def calcular_kpi_ementa(session: Session, ementa_id: int) -> EmentaKPIDTO:
        """
        Calcula a percentagem média de produtos biológicos para uma ementa completa
        """
        ementa = session.query(EmentaORM).filter(EmentaORM.id == ementa_id).first()
        
        if not ementa:
            raise ValueError(f"Ementa com ID {ementa_id} não encontrada")
        
        dias_kpi = []
        percentagens_dias = []
        
        # Calcular para cada dia da semana (1-5 = Segunda a Sexta)
        for dia_semana in range(1, 6):
            try:
                dia_kpi = KPIService.calcular_kpi_dia(session, ementa_id, dia_semana)
                dias_kpi.append(dia_kpi)
                percentagens_dias.append(dia_kpi.media_percentagem_biologica)
            except:
                # Dia sem refeições, skip
                pass
        
        media_total = mean(percentagens_dias) if percentagens_dias else 0.0
        
        return EmentaKPIDTO(
            ementa_id=ementa_id,
            ementa_nome=ementa.nome,
            media_percentagem_biologica=round(media_total, 2),
            dias=dias_kpi
        )
    
    # ==== MÉTODOS DE DESPERDÍCIO ====
    
    @staticmethod
    def calcular_desperdicio_refeicao(session: Session, refeicao_id: int, data_execucao: date = None) -> DesperdícioRefeicaoDTO:
        """
        Calcula desperdício de uma refeição específica.
        Se data_execucao não for fornecida, usa a mais recente.
        """
        refeicao = session.query(RefeicaoORM).filter(RefeicaoORM.id == refeicao_id).first()
        
        if not refeicao:
            raise ValueError(f"Refeição com ID {refeicao_id} não encontrada")
        
        # Buscar execução da refeição
        query = session.query(ExecucaoRefeicaoORM).filter(
            ExecucaoRefeicaoORM.refeicao_id == refeicao_id
        )
        
        if data_execucao:
            execucao = query.filter(ExecucaoRefeicaoORM.data_execucao == data_execucao).first()
        else:
            execucao = query.order_by(ExecucaoRefeicaoORM.data_execucao.desc()).first()
        
        if not execucao:
            # Se não tem execução, retornar dados zerados
            return DesperdícioRefeicaoDTO(
                refeicao_id=refeicao_id,
                refeicao_descricao=refeicao.descricao or "",
                data_execucao=str(date.today()),
                quantidade_produzida=0,
                quantidade_servida=0,
                quantidade_nao_servida=0,
                taxa_desperdicio=0.0,
                taxa_servida=0.0
            )
        
        total_prod = execucao.quantidade_produzida
        total_serv = execucao.quantidade_servida
        total_nao_serv = execucao.quantidade_nao_servida
        
        taxa_desp = (total_nao_serv / total_prod * 100) if total_prod > 0 else 0.0
        taxa_serv = (total_serv / total_prod * 100) if total_prod > 0 else 0.0
        
        return DesperdícioRefeicaoDTO(
            refeicao_id=refeicao_id,
            refeicao_descricao=refeicao.descricao or "",
            data_execucao=str(execucao.data_execucao),
            quantidade_produzida=total_prod,
            quantidade_servida=total_serv,
            quantidade_nao_servida=total_nao_serv,
            taxa_desperdicio=round(taxa_desp, 2),
            taxa_servida=round(taxa_serv, 2)
        )
    
    @staticmethod
    def calcular_desperdicio_dia(session: Session, ementa_id: int, dia_semana: int) -> DesperdícioDiaDTO:
        """
        Calcula desperdício agregado de um dia (almoço + jantar)
        """
        refeicoes = session.query(RefeicaoORM).filter(
            RefeicaoORM.ementa_id == ementa_id,
            RefeicaoORM.dia_semana == dia_semana
        ).all()
        
        if not refeicoes:
            return DesperdícioDiaDTO(
                ementa_id=ementa_id,
                dia_semana=dia_semana,
                tipo_refeicao="completo",
                total_produzido=0,
                total_servido=0,
                total_nao_servido=0,
                taxa_desperdicio_media=0.0,
                taxa_servida_media=0.0
            )
        
        totais_prod = 0
        totais_serv = 0
        totais_nao_serv = 0
        taxas_desp = []
        
        for refeicao in refeicoes:
            execucoes = session.query(ExecucaoRefeicaoORM).filter(
                ExecucaoRefeicaoORM.refeicao_id == refeicao.id
            ).all()
            
            for exec in execucoes:
                totais_prod += exec.quantidade_produzida
                totais_serv += exec.quantidade_servida
                totais_nao_serv += exec.quantidade_nao_servida
                
                if exec.quantidade_produzida > 0:
                    taxa = (exec.quantidade_nao_servida / exec.quantidade_produzida * 100)
                    taxas_desp.append(taxa)
        
        taxa_desp_media = mean(taxas_desp) if taxas_desp else 0.0
        taxa_serv_media = (totais_serv / totais_prod * 100) if totais_prod > 0 else 0.0
        
        # Determinar tipo de refeição
        tipos = set(r.tipo for r in refeicoes)
        tipo_str = " + ".join(sorted(tipos)) if tipos else "completo"
        
        return DesperdícioDiaDTO(
            ementa_id=ementa_id,
            dia_semana=dia_semana,
            tipo_refeicao=tipo_str,
            total_produzido=totais_prod,
            total_servido=totais_serv,
            total_nao_servido=totais_nao_serv,
            taxa_desperdicio_media=round(taxa_desp_media, 2),
            taxa_servida_media=round(taxa_serv_media, 2)
        )
    
    @staticmethod
    def calcular_desperdicio_ementa(session: Session, ementa_id: int) -> DesperdícioEmentaDTO:
        """
        Calcula desperdício agregado de uma ementa completa
        """
        ementa = session.query(EmentaORM).filter(EmentaORM.id == ementa_id).first()
        
        if not ementa:
            raise ValueError(f"Ementa com ID {ementa_id} não encontrada")
        
        dias_desp = []
        totais_prod = 0
        totais_serv = 0
        totais_nao_serv = 0
        
        # Calcular para cada dia da semana (1-5)
        for dia_semana in range(1, 6):
            try:
                dia_desp = KPIService.calcular_desperdicio_dia(session, ementa_id, dia_semana)
                if dia_desp.total_produzido > 0:  # Apenas incluir dias com dados
                    dias_desp.append(dia_desp)
                    totais_prod += dia_desp.total_produzido
                    totais_serv += dia_desp.total_servido
                    totais_nao_serv += dia_desp.total_nao_servido
            except:
                pass
        
        taxa_desp_geral = (totais_nao_serv / totais_prod * 100) if totais_prod > 0 else 0.0
        taxa_serv_geral = (totais_serv / totais_prod * 100) if totais_prod > 0 else 0.0
        
        return DesperdícioEmentaDTO(
            ementa_id=ementa_id,
            ementa_nome=ementa.nome,
            total_produzido=totais_prod,
            total_servido=totais_serv,
            total_nao_servido=totais_nao_serv,
            taxa_desperdicio_geral=round(taxa_desp_geral, 2),
            taxa_servida_geral=round(taxa_serv_geral, 2),
            dias=dias_desp
        )
    
    @staticmethod
    @staticmethod
    def calcular_kpi_consolidado(session: Session, ementa_id: int) -> KPIConsolidadoDTO:
        """
        Retorna KPI consolidado: biológico + desperdício
        """
        # Calcular biológico
        kpi_bio = KPIService.calcular_kpi_ementa(session, ementa_id)
        
        # Calcular desperdício
        kpi_desp = KPIService.calcular_desperdicio_ementa(session, ementa_id)
        
        return KPIConsolidadoDTO(
            ementa_id=ementa_id,
            ementa_nome=kpi_bio.ementa_nome,
            percentagem_biologica=kpi_bio.media_percentagem_biologica,
            taxa_desperdicio=kpi_desp.taxa_desperdicio_geral,
            taxa_servida=kpi_desp.taxa_servida_geral,
            total_produzido=kpi_desp.total_produzido,
            total_servido=kpi_desp.total_servido,
            total_nao_servido=kpi_desp.total_nao_servido
        )