import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta


def get_todas_cantinas_kpi(api_url, auth_token, data_inicio, data_fim):
    """Obtém KPI de todas as cantinas."""
    try:
        response = requests.get(
            f"{api_url}/unidades/kpis/cantinas",
            params={"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_kpi_cantina(api_url, auth_token, cantina_id, data_inicio, data_fim):
    """Obtém KPI de uma cantina específica."""
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


def pagina_administrador_kpi(API_URL, auth_token):
    """Dashboard KPI para Administrador - visão consolidada de todas as cantinas."""
    st.set_page_config(page_title="Administrador - KPI Consolidado", layout="wide")
    st.header("📊 Dashboard KPI Consolidado - Administrador")

    # Período de análise
    col1, col2, col3 = st.columns(3)
    with col1:
        data_fim = st.date_input("Data Fim", value=date.today(), key="admin_kpi_data_fim")
    with col2:
        num_dias = st.number_input("Últimos N dias", min_value=1, max_value=365, value=30, key="admin_kpi_dias")
    with col3:
        data_inicio = data_fim - timedelta(days=num_dias)
        st.write(f"**Desde:** {data_inicio.strftime('%d/%m/%Y')}")

    st.divider()

    # Obter KPIs de todas as cantinas
    kpis_data = get_todas_cantinas_kpi(API_URL, auth_token, data_inicio, data_fim)
    
    if not kpis_data or not kpis_data.get("cantinas"):
        st.warning("Nenhuma cantina encontrada no período especificado.")
        return

    cantinas = kpis_data["cantinas"]

    # ===== TAB 1: SUMÁRIO CONSOLIDADO =====
    tab1, tab2, tab3 = st.tabs(["📈 Sumário Consolidado", "🏢 Comparação Cantinas", "🔍 Detalhes"])

    with tab1:
        st.subheader("Sumário Consolidado de Todas as Cantinas")
        
        # Calcular totais
        total_servidas = sum(c['refeicoes_servidas'] for c in cantinas)
        total_desperdiçadas = sum(c['refeicoes_desperdiçadas'] for c in cantinas)
        media_conformidade = sum(c['conformidade_plano_pct'] for c in cantinas) / len(cantinas) if cantinas else 0
        media_desperdicio = sum(c['taxa_desperdicio_pct'] for c in cantinas) / len(cantinas) if cantinas else 0
        total_produzidas = sum(c['refeicoes_produzidas'] for c in cantinas)

        # Métricas em 5 colunas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "🍽️ Total Servidas",
                f"{total_servidas:,}",
                f"{len(cantinas)} cantinas"
            )
        
        with col2:
            st.metric(
                "🗑️ Total Desperdiçadas",
                f"{total_desperdiçadas:,}",
                f"{media_desperdicio:.1f}% média"
            )
        
        with col3:
            st.metric(
                "📊 Conformidade Média",
                f"{media_conformidade:.1f}%",
                "de todas cantinas"
            )
        
        with col4:
            st.metric(
                "🏭 Total Produzidas",
                f"{total_produzidas:,}",
                "período"
            )
        
        with col5:
            st.metric(
                "🏢 Cantinas",
                f"{len(cantinas)}",
                "no sistema"
            )

        st.divider()

        # Gráficos consolidados
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Refeições: Servidas vs Desperdiçadas")
            dados_consolidado = {
                "Servidas": total_servidas,
                "Desperdiçadas": total_desperdiçadas,
            }
            st.bar_chart(dados_consolidado)
        
        with col_right:
            st.subheader("Métricas Médias")
            dados_medias = {
                "Conformidade %": media_conformidade,
                "Desperdício %": media_desperdicio,
            }
            st.bar_chart(dados_medias)

    # ===== TAB 2: COMPARAÇÃO CANTINAS =====
    with tab2:
        st.subheader("Comparação entre Cantinas")
        
        # Tabela comparativa
        dados_tabela = []
        for cantina in cantinas:
            dados_tabela.append({
                "Cantina": cantina['cantina_nome'],
                "Tipo": cantina['tipo'],
                "Servidas": cantina['refeicoes_servidas'],
                "Desperdiçadas": cantina['refeicoes_desperdiçadas'],
                "Taxa Desperdício %": cantina['taxa_desperdicio_pct'],
                "Conformidade %": cantina['conformidade_plano_pct'],
                "Execuções": cantina['num_execucoes'],
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # Gráficos comparativos
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Taxa de Desperdício por Cantina")
            df_desperdicio = df.set_index("Cantina")[["Taxa Desperdício %"]].sort_values("Taxa Desperdício %", ascending=False)
            st.bar_chart(df_desperdicio)
        
        with col_right:
            st.subheader("Conformidade do Plano por Cantina")
            df_conformidade = df.set_index("Cantina")[["Conformidade %"]].sort_values("Conformidade %", ascending=False)
            st.bar_chart(df_conformidade)

    # ===== TAB 3: DETALHES CANTINA =====
    with tab3:
        st.subheader("Detalhes de Cantina Específica")
        
        # Seletor de cantina
        cantina_nomes = {c['cantina_nome']: c['cantina_id'] for c in cantinas}
        cantina_selecionada_nome = st.selectbox(
            "Selecione uma cantina",
            options=list(cantina_nomes.keys()),
            key="admin_cantina_select"
        )
        
        cantina_id = cantina_nomes[cantina_selecionada_nome]
        
        # Obter detalhes da cantina
        kpi_detalhado = get_kpi_cantina(API_URL, auth_token, cantina_id, data_inicio, data_fim)
        
        if kpi_detalhado and "erro" not in kpi_detalhado:
            # Informações da cantina
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Informações da Cantina:**")
                st.write(f"- Nome: {kpi_detalhado['cantina_nome']}")
                st.write(f"- Tipo: {kpi_detalhado['tipo']}")
            
            with col2:
                st.write("**Período de Análise:**")
                st.write(f"- Início: {kpi_detalhado['periodo']['data_inicio']}")
                st.write(f"- Fim: {kpi_detalhado['periodo']['data_fim']}")
                st.write(f"- Dias: {kpi_detalhado['num_dias']}")

            st.divider()

            # Métricas detalhadas
            st.subheader("📊 Métricas Detalhadas")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Refeições Servidas", f"{kpi_detalhado['refeicoes_servidas']:,}")
            with col2:
                st.metric("Refeições Desperdiçadas", f"{kpi_detalhado['refeicoes_desperdiçadas']:,}")
            with col3:
                st.metric("Refeições Produzidas", f"{kpi_detalhado['refeicoes_produzidas']:,}")
            with col4:
                st.metric("Execuções Registadas", f"{kpi_detalhado['num_execucoes']}")

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Taxa Desperdício", f"{kpi_detalhado['taxa_desperdicio_pct']:.1f}%")
            with col2:
                st.metric("Conformidade Plano", f"{kpi_detalhado['conformidade_plano_pct']:.1f}%")
            with col3:
                if kpi_detalhado['num_execucoes'] > 0:
                    media = kpi_detalhado['refeicoes_servidas'] // kpi_detalhado['num_execucoes']
                    st.metric("Média Refeições/Execução", f"{media:,}")

        else:
            st.warning("Sem dados detalhados para esta cantina no período especificado.")

    st.divider()

    # Análise de Tendências
    st.subheader("📈 Análise de Desempenho")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cantinas com Melhor Desempenho (Menor Desperdício):**")
        top_5_desperdicio = df.nsmallest(5, "Taxa Desperdício %")[["Cantina", "Taxa Desperdício %"]]
        st.dataframe(top_5_desperdicio, hide_index=True)
    
    with col2:
        st.write("**Cantinas com Maior Conformidade:**")
        top_5_conformidade = df.nlargest(5, "Conformidade %")[["Cantina", "Conformidade %"]]
        st.dataframe(top_5_conformidade, hide_index=True)

    st.divider()

    # Alertas
    st.subheader("⚠️ Alertas e Recomendações")
    
    alertas = []
    
    # Verificar cantinas com desperdício crítico
    criticas_desperdicio = df[df["Taxa Desperdício %"] > 20]
    if not criticas_desperdicio.empty:
        alertas.append(f"🔴 {len(criticas_desperdicio)} cantina(s) com taxa de desperdício > 20%: {', '.join(criticas_desperdicio['Cantina'].tolist())}")
    
    # Verificar cantinas com baixa conformidade
    criticas_conformidade = df[df["Conformidade %"] < 80]
    if not criticas_conformidade.empty:
        alertas.append(f"🟡 {len(criticas_conformidade)} cantina(s) com conformidade < 80%: {', '.join(criticas_conformidade['Cantina'].tolist())}")
    
    # Desperdício médio muito alto
    if media_desperdicio > 15:
        alertas.append(f"⚠️ Taxa média de desperdício muito alta ({media_desperdicio:.1f}%). Revisar processos em todas cantinas.")
    
    # Conformidade média baixa
    if media_conformidade < 85:
        alertas.append(f"⚠️ Conformidade média baixa ({media_conformidade:.1f}%). Melhorar seguimento de ementas.")
    
    if alertas:
        for alerta in alertas:
            st.warning(alerta)
    else:
        st.success("✅ Nenhum alerta crítico. Sistema funcionando dentro dos parâmetros esperados.")
