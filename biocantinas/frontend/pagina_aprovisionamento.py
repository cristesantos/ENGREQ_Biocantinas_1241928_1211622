import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd

API_BASE = "http://localhost:8000"

def mostrar_aprovisionamento():
    st.title("📦 Aprovisionamento de Produtos")
    st.write("Sistema de cálculo de necessidades e gestão de pedidos aos fornecedores")
    
    # Verificar permissão
    user_info = st.session_state.get("user_info", {})
    role = user_info.get("role", "")
    
    if role != "GESTOR_CANTINA":
        st.error("⛔ **Acesso Restrito**")
        st.info("Esta página é exclusiva para o Gestor da Cantina.")
        return
    
    token = st.session_state.get("auth_token")
    
    if not token:
        st.error("❌ Token de autenticação não encontrado. Faça login novamente.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Preview de Necessidades",
        "✅ Plano de Produção",
        "📮 Pedidos aos Fornecedores",
        "⚠️ Alertas"
    ])
    
    # ============ TAB 1: PREVIEW DE NECESSIDADES ============
    with tab1:
        st.subheader("🔍 Preview de Necessidades (Visualização)")
        st.write("Visualize as necessidades sem salvar no banco de dados")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(
                "Data Início",
                value=date.today(),
                key="preview_inicio"
            )
        with col2:
            data_fim = st.date_input(
                "Data Fim",
                value=date.today() + timedelta(days=7),
                key="preview_fim"
            )
        
        if st.button("🔍 Ver Preview", key="btn_preview"):
            try:
                response = requests.get(
                    f"{API_BASE}/aprovisionamento/preview",
                    params={
                        "data_inicio": str(data_inicio),
                        "data_fim": str(data_fim)
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    st.success(f"✅ Preview gerado para {dados['periodo']}")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**📊 Necessidades Planejadas**")
                        st.caption("(Baseado nas ementas criadas)")
                        if dados["necessidades_planejadas"]:
                            df_planejadas = pd.DataFrame(
                                list(dados["necessidades_planejadas"].items()),
                                columns=["Produto", "Quantidade (kg)"]
                            )
                            st.dataframe(df_planejadas, use_container_width=True)
                        else:
                            st.info("Nenhuma ementa planejada para este período")
                    
                    with col_b:
                        st.markdown("**📈 Necessidades com Reservas**")
                        st.caption("(Ajustado com reservas de estudantes)")
                        if dados["necessidades_com_reservas"]:
                            df_reservas = pd.DataFrame(
                                list(dados["necessidades_com_reservas"].items()),
                                columns=["Produto", "Quantidade (kg)"]
                            )
                            st.dataframe(df_reservas, use_container_width=True)
                        else:
                            st.info("Nenhuma reserva registrada")
                    
                    # Mostrar desvios
                    st.markdown("**📉 Desvios Percentuais**")
                    if dados.get("desvios_percentuais"):
                        desvios_data = [
                            {
                                "Produto": prod,
                                "Desvio (%)": f"{desvio:+.1f}%",
                                "Status": "⚠️ Alerta" if abs(desvio) > 10 else "✅ OK"
                            }
                            for prod, desvio in dados["desvios_percentuais"].items()
                        ]
                        st.dataframe(pd.DataFrame(desvios_data), use_container_width=True)
                
                else:
                    st.error(f"❌ Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
            
            except Exception as e:
                st.error(f"❌ Erro ao conectar com API: {str(e)}")
    
    # ============ TAB 2: PLANO DE PRODUÇÃO ============
    with tab2:
        st.subheader("✅ Calcular Plano de Produção Final")
        st.write("Calcula e **salva** o plano de produção no banco de dados")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio_plano = st.date_input(
                "Data Início",
                value=date.today(),
                key="plano_inicio"
            )
        with col2:
            data_fim_plano = st.date_input(
                "Data Fim",
                value=date.today() + timedelta(days=7),
                key="plano_fim"
            )
        
        st.warning("⚠️ **Atenção:** Esta ação irá salvar o plano de produção no banco de dados.")
        
        if st.button("✅ Calcular e Salvar Plano", type="primary", key="btn_plano"):
            try:
                response = requests.post(
                    f"{API_BASE}/aprovisionamento/calcular-plano",
                    params={
                        "data_inicio": str(data_inicio_plano),
                        "data_fim": str(data_fim_plano)
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    
                    st.success(f"✅ Plano calculado e salvo com sucesso!")
                    
                    # Métricas
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Total de Produtos", resultado.get("total_produtos", 0))
                    with col_m2:
                        st.metric("Produtos com Alerta", resultado.get("produtos_com_alerta", 0))
                    with col_m3:
                        st.metric("Período", resultado.get("periodo", ""))
                    
                    # Alertas
                    if resultado.get("alertas"):
                        st.warning(f"⚠️ **{len(resultado['alertas'])} alertas de desvio > 10%**")
                        for alerta in resultado["alertas"]:
                            st.write(f"- {alerta['mensagem']}")
                    else:
                        st.success("✅ Nenhum alerta de desvio significativo")
                    
                    # Tabela do plano
                    if resultado.get("plano"):
                        st.markdown("**📋 Plano Detalhado**")
                        df_plano = pd.DataFrame(resultado["plano"])
                        st.dataframe(df_plano, use_container_width=True)
                
                else:
                    st.error(f"❌ Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
            
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    # ============ TAB 3: PEDIDOS AOS FORNECEDORES ============
    with tab3:
        st.subheader("📮 Gerar Pedidos aos Fornecedores")
        st.write("Cria pedidos automaticamente com ordem de prioridade por data de inscrição")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            data_inicio_pedido = st.date_input(
                "Data Início (Período)",
                value=date.today(),
                key="pedido_inicio"
            )
        with col2:
            data_fim_pedido = st.date_input(
                "Data Fim (Período)",
                value=date.today() + timedelta(days=7),
                key="pedido_fim"
            )
        with col3:
            data_entrega = st.date_input(
                "Data de Entrega Desejada",
                value=date.today() + timedelta(days=3),
                key="data_entrega"
            )
        
        if st.button("📮 Gerar Pedidos", type="primary", key="btn_pedidos"):
            try:
                response = requests.post(
                    f"{API_BASE}/aprovisionamento/gerar-pedidos",
                    params={
                        "data_inicio": str(data_inicio_pedido),
                        "data_fim": str(data_fim_pedido),
                        "data_entrega": str(data_entrega)
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    
                    st.success(f"✅ {resultado.get('total', 0)} pedidos criados com sucesso!")
                    
                    if resultado.get("pedidos_criados"):
                        df_pedidos = pd.DataFrame(resultado["pedidos_criados"])
                        st.dataframe(df_pedidos, use_container_width=True)
                    
                    if resultado.get("erros"):
                        st.warning("⚠️ **Erros encontrados:**")
                        for erro in resultado["erros"]:
                            st.write(f"- {erro}")
                
                else:
                    st.error(f"❌ Erro {response.status_code}")
            
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
        
        # Listar pedidos existentes
        st.markdown("---")
        st.subheader("📋 Pedidos Existentes")
        
        status_filtro = st.selectbox(
            "Filtrar por status",
            ["Todos", "pendente", "confirmado", "entregue"],
            key="filtro_status"
        )
        
        if st.button("🔄 Atualizar Lista", key="btn_atualizar"):
            try:
                params = {} if status_filtro == "Todos" else {"status": status_filtro}
                
                response = requests.get(
                    f"{API_BASE}/aprovisionamento/pedidos",
                    params=params,
                    headers=headers
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    if dados.get("pedidos"):
                        df = pd.DataFrame(dados["pedidos"])
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"Total: {dados.get('total', 0)} pedidos")
                    else:
                        st.info("Nenhum pedido encontrado")
                
                else:
                    st.error(f"❌ Erro {response.status_code}")
            
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    # ============ TAB 4: ALERTAS ============
    with tab4:
        st.subheader("⚠️ Alertas de Desvio > 10%")
        st.write("Lista de produtos com desvio significativo entre planejado e realizado")
        
        if st.button("🔄 Carregar Alertas", key="btn_alertas"):
            try:
                response = requests.get(
                    f"{API_BASE}/aprovisionamento/alertas",
                    headers=headers
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    total = dados.get("total_alertas", 0)
                    
                    if total > 0:
                        st.warning(f"⚠️ **{total} alertas encontrados**")
                        
                        alertas_data = dados.get("alertas", [])
                        if alertas_data:
                            df_alertas = pd.DataFrame(alertas_data)
                            st.dataframe(df_alertas, use_container_width=True)
                    else:
                        st.success("✅ Nenhum alerta de desvio significativo")
                
                else:
                    st.error(f"❌ Erro {response.status_code}")
            
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")


if __name__ == "__main__":
    # Para teste standalone
    st.session_state["role"] = "GESTOR_CANTINA"
    st.session_state["token"] = "test_token"
    mostrar_aprovisionamento()
