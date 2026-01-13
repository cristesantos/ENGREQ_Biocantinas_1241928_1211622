import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta


def get_kpi_cantina(api_url, auth_token, cantina_id, data_inicio, data_fim):
    """Obtém KPI de uma cantina."""
    try:
        response = requests.get(
            f"{api_url}/unidades/kpis/cantinas/{cantina_id}",
            params={"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_kpis_refeitorios(api_url, auth_token, cantina_id, data_inicio, data_fim):
    """Obtém KPIs de todos os refeitórios de uma cantina."""
    try:
        response = requests.get(
            f"{api_url}/unidades/kpis/cantinas/{cantina_id}/refeitorios",
            params={"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_todas_cantinas(api_url, auth_token):
    """Obtém lista de todas as cantinas."""
    try:
        response = requests.get(
            f"{api_url}/unidades/cantinas",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_refeitorios(api_url, auth_token):
    """Obtém lista de todos os refeitórios."""
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


def pagina_gestor_cantina(API_URL, auth_token):
    """Dashboard KPI para Gestor de Cantina."""
    st.set_page_config(page_title="Gestor Cantina - KPI", layout="wide")
    st.header("📊 Dashboard KPI - Gestor da Cantina")

    # Período de análise
    col1, col2, col3 = st.columns(3)
    with col1:
        data_fim = st.date_input("Data Fim", value=date.today(), key="gestor_cantina_data_fim")
    with col2:
        num_dias = st.number_input("Últimos N dias", min_value=1, max_value=365, value=30, key="gestor_cantina_dias")
    with col3:
        data_inicio = data_fim - timedelta(days=num_dias)
        st.write(f"**Desde:** {data_inicio.strftime('%d/%m/%Y')}")

    st.divider()

    # Obter cantinas
    cantinas = get_todas_cantinas(API_URL, auth_token)
    
    if not cantinas:
        st.error("Nenhuma cantina encontrada.")
        return

    # Filtrar apenas cantinas locais (não central)
    cantinas_locais = [c for c in cantinas if c.get("tipo") == "LOCAL"]
    
    if not cantinas_locais:
        st.info("Você não tem cantinas associadas.")
        return

    # Selecionar cantina
    cantina_selecionada = st.selectbox(
        "Selecione a sua Cantina",
        options=cantinas_locais,
        format_func=lambda x: f"{x['nome']} ({x['localizacao']})",
        key="gestor_cantina_select"
    )

    st.divider()

    # Tab 1: KPI da Cantina
    tab1, tab2 = st.tabs(["📈 KPI da Cantina", "🏢 KPIs dos Refeitórios"])

    with tab1:
        st.subheader(f"KPI - {cantina_selecionada['nome']}")
        
        kpi = get_kpi_cantina(API_URL, auth_token, cantina_selecionada['id'], data_inicio, data_fim)
        
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
                    f"período"
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

            # Detalhes
            st.subheader("📋 Detalhes do Período")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Tipo Cantina:** {kpi['tipo']}")
            with col2:
                st.write(f"**Período:** {kpi['periodo']['data_inicio']} a {kpi['periodo']['data_fim']}")
            with col3:
                st.write(f"**Duração:** {kpi['num_dias']} dias")

        else:
            st.warning("Sem dados de KPI para este período.")

    with tab2:
        st.subheader("KPIs dos Refeitórios")
        
        kpis_ref = get_kpis_refeitorios(API_URL, auth_token, cantina_selecionada['id'], data_inicio, data_fim)
        
        if kpis_ref and kpis_ref.get("refeitorios"):
            refeitorios = kpis_ref["refeitorios"]
            
            # Tabela comparativa
            dados_tabela = []
            for ref in refeitorios:
                dados_tabela.append({
                    "Refeitório": ref['refeitorio_nome'],
                    "Servidas": ref['refeicoes_servidas'],
                    "Desperdiçadas": ref['refeicoes_desperdiçadas'],
                    "Taxa Desperdício %": ref['taxa_desperdicio_pct'],
                    "Conformidade %": ref['conformidade_plano_pct'],
                    "Execuções": ref['num_execucoes'],
                })
            
            df = pd.DataFrame(dados_tabela)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Gráfico comparativo
            st.subheader("Comparação de Taxa de Desperdício")
            df_chart = df.set_index("Refeitório")[["Taxa Desperdício %"]]
            st.bar_chart(df_chart)

        else:
            st.info("Nenhum refeitório encontrado para esta cantina.")
