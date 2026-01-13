import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta


def get_kpi_refeitorio(api_url, auth_token, refeitorio_id, data_inicio, data_fim):
    """Obtém KPI de um refeitório."""
    try:
        response = requests.get(
            f"{api_url}/unidades/kpis/refeitorios/{refeitorio_id}",
            params={"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_refeitorios_user(api_url, auth_token):
    """Obtém lista de refeitórios do utilizador."""
    try:
        response = requests.get(
            f"{api_url}/unidades/refeitorios",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def pagina_gestor_refeitorio(API_URL, auth_token):
    """Dashboard KPI para Gestor de Refeitório."""
    st.set_page_config(page_title="Gestor Refeitório - KPI", layout="wide")
    st.header("📊 Dashboard KPI - Gestor do Refeitório")

    # Período de análise
    col1, col2, col3 = st.columns(3)
    with col1:
        data_fim = st.date_input("Data Fim", value=date.today(), key="gestor_ref_data_fim")
    with col2:
        num_dias = st.number_input("Últimos N dias", min_value=1, max_value=365, value=30, key="gestor_ref_dias")
    with col3:
        data_inicio = data_fim - timedelta(days=num_dias)
        st.write(f"**Desde:** {data_inicio.strftime('%d/%m/%Y')}")

    st.divider()

    # Obter refeitórios
    refeitorios = get_refeitorios_user(API_URL, auth_token)
    
    if not refeitorios:
        st.error("Nenhum refeitório encontrado.")
        return

    # Selecionar refeitório
    refeitorio_selecionado = st.selectbox(
        "Selecione o seu Refeitório",
        options=refeitorios,
        format_func=lambda x: f"{x['nome']} ({x['localizacao']})",
        key="gestor_ref_select"
    )

    st.divider()

    # KPI do Refeitório
    st.subheader(f"📈 KPI - {refeitorio_selecionado['nome']}")
    
    kpi = get_kpi_refeitorio(API_URL, auth_token, refeitorio_selecionado['id'], data_inicio, data_fim)
    
    if kpi and "erro" not in kpi:
        # Métricas principais em 4 colunas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🍽️ Refeições Servidas",
                f"{kpi['refeicoes_servidas']:,}",
                f"{kpi['num_dias']} dias"
            )
        
        with col2:
            st.metric(
                "🗑️ Refeições Desperdiçadas",
                f"{kpi['refeicoes_desperdiçadas']:,}",
                f"{kpi['taxa_desperdicio_pct']}%"
            )
        
        with col3:
            st.metric(
                "📊 Conformidade Plano",
                f"{kpi['conformidade_plano_pct']:.1f}%",
                f"de {kpi['refeicoes_produzidas']:,} produzidas"
            )
        
        with col4:
            st.metric(
                "✅ Execuções Registadas",
                f"{kpi['num_execucoes']}",
                f"no período"
            )

        st.divider()

        # Gráficos
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Distribuição de Refeições")
            dados = {
                "Servidas": kpi['refeicoes_servidas'],
                "Desperdiçadas": kpi['refeicoes_desperdiçadas'],
            }
            st.bar_chart(dados)
        
        with col_right:
            st.subheader("Conformidade vs Taxa de Desperdício")
            dados = {
                "Conformidade %": kpi['conformidade_plano_pct'],
                "Desperdício %": kpi['taxa_desperdicio_pct'],
            }
            st.bar_chart(dados)

        st.divider()

        # Análise detalhada
        st.subheader("📋 Análise Detalhada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Informações do Refeitório:**")
            st.write(f"- Nome: {refeitorio_selecionado['nome']}")
            st.write(f"- Localização: {refeitorio_selecionado['localizacao']}")
            st.write(f"- Período: {kpi['periodo']['data_inicio']} a {kpi['periodo']['data_fim']}")
        
        with col2:
            st.write("**Sumário de Desempenho:**")
            st.write(f"- Total dias: {kpi['num_dias']}")
            st.write(f"- Execuções registadas: {kpi['num_execucoes']}")
            if kpi['num_execucoes'] > 0:
                media_refeicoes = kpi['refeicoes_servidas'] // kpi['num_execucoes']
                st.write(f"- Média refeições/execução: {media_refeicoes}")

        st.divider()

        # Indicadores de Performance
        st.subheader("🎯 Indicadores de Performance")
        
        # Cor baseada em conformidade
        if kpi['conformidade_plano_pct'] >= 95:
            conformidade_status = "✅ Excelente"
            conformidade_color = "green"
        elif kpi['conformidade_plano_pct'] >= 85:
            conformidade_status = "⚠️ Bom"
            conformidade_color = "yellow"
        else:
            conformidade_status = "🔴 Crítico"
            conformidade_color = "red"

        # Cor baseada em desperdício
        if kpi['taxa_desperdicio_pct'] <= 5:
            desperdicio_status = "✅ Baixo"
            desperdicio_color = "green"
        elif kpi['taxa_desperdicio_pct'] <= 15:
            desperdicio_status = "⚠️ Moderado"
            desperdicio_color = "yellow"
        else:
            desperdicio_status = "🔴 Alto"
            desperdicio_color = "red"

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### Conformidade do Plano: {conformidade_status}")
            st.progress(min(kpi['conformidade_plano_pct'] / 100, 1.0))
        with col2:
            st.markdown(f"### Taxa de Desperdício: {desperdicio_status}")
            st.progress(min(kpi['taxa_desperdicio_pct'] / 100, 1.0))

        # Recomendações
        st.divider()
        st.subheader("💡 Recomendações")
        
        recomendacoes = []
        
        if kpi['taxa_desperdicio_pct'] > 15:
            recomendacoes.append("🗑️ Taxa de desperdício acima do esperado. Revise os processos de preparação e servição.")
        
        if kpi['conformidade_plano_pct'] < 85:
            recomendacoes.append("📊 Conformidade do plano baixa. Verifique se as ementas estão sendo seguidas.")
        
        if kpi['refeicoes_desperdiçadas'] > 0 and kpi['refeicoes_servidas'] > 0:
            if (kpi['refeicoes_desperdiçadas'] / kpi['refeicoes_servidas']) > 0.2:
                recomendacoes.append("⚠️ Proporção desperdício/servidas é alta. Considere revisar quantidades preparadas.")
        
        if not recomendacoes:
            st.success("✅ Desempenho dentro dos parâmetros esperados. Parabéns!")
        else:
            for rec in recomendacoes:
                st.info(rec)

    else:
        st.warning("Sem dados de KPI para este período.")
