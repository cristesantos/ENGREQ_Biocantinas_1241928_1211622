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
    tab1, tab2 = st.tabs([
        "🔍 Previsão de Necessidades",
        "📋 Ordem de Fornecimento"
    ])
    
    # ============ TAB 1: PREVISÃO DE NECESSIDADES ============
    with tab1:
        st.subheader("🔍 Previsão de Necessidades (Visualização)")
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
                    
                    # Linha 1: Ementa e Necessidades Planejadas lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📋 Ementa do Período**")
                        if dados.get("refeicoes_detalhes"):
                            ementa_html = "<div style='font-size: 0.85em; line-height: 1.3;'>"
                            for refeicao in dados["refeicoes_detalhes"]:
                                data_label = refeicao.get('data', '')
                                dia_semana = refeicao.get('dia_semana', '')
                                ementa_html += f"<p style='margin: 8px 0 2px 0;'><b>📅 {data_label} ({dia_semana}) - {refeicao['tipo'].title()}</b><br>"
                                ementa_html += f"<i>{refeicao['descricao']}</i></p>"
                                ementa_html += "<ul style='margin: 2px 0 8px 0; padding-left: 20px;'>"
                                for ing in refeicao['ingredientes']:
                                    ementa_html += f"<li>{ing['ingrediente']}: {ing.get('quantidade_estimada', ing.get('quantidade', 0))} kg</li>"
                                ementa_html += "</ul><hr style='margin: 4px 0;'>"
                            ementa_html += "</div>"
                            st.markdown(ementa_html, unsafe_allow_html=True)
                        else:
                            st.info("Sem ementas")
                    
                    with col2:
                        st.markdown("**📊 Necessidades Planejadas**")
                        st.caption("Quantidade total de produtos com histórico aplicado")
                        if dados.get("necessidades_previstas_historico"):
                            df_planejadas = pd.DataFrame(
                                list(dados["necessidades_previstas_historico"].items()),
                                columns=["Produto", "Quantidade (kg)"]
                            )
                            st.dataframe(df_planejadas, width='stretch')
                        else:
                            st.info("Sem histórico")
                    
                    st.divider()
                    
                    # Linha 2: Histórico de Reservas (largura total)
                    st.markdown("**📈 Histórico de Reservas**")
                    st.caption("Dados históricos por prato do período")
                    if dados.get("historico_detalhes"):
                        df_historico = pd.DataFrame(dados["historico_detalhes"])
                        # Calcular altura baseada no número de refeições (aproximadamente 35px por linha + header)
                        num_refeicoes = len(dados.get("refeicoes_detalhes", []))
                        altura_historico = min(max(num_refeicoes * 35 + 38, 150), 400)
                        
                        # Configurar colunas com larguras personalizadas
                        column_config = {
                            "Data": st.column_config.TextColumn("Data", width="small"),
                            "Dia Semana": st.column_config.TextColumn("Dia Semana", width="small"),
                            "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                            "Descrição": st.column_config.TextColumn("Descrição", width="large"),
                            "Previsão": st.column_config.NumberColumn("Previsão", width="small"),
                            "Reservas Reais": st.column_config.NumberColumn("Reservas Reais", width="small")
                        }
                        
                        st.dataframe(
                            df_historico, 
                            width='stretch', 
                            height=altura_historico,
                            column_config=column_config,
                            hide_index=True
                        )
                    else:
                        st.info("Sem dados históricos")
                
                else:
                    st.error(f"❌ Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
            
            except Exception as e:
                st.error(f"❌ Erro ao conectar com API: {str(e)}")
    
    # ============ TAB 2: ORDEM DE FORNECIMENTO ============
    with tab2:
        st.subheader("📋 Ordem de Fornecimento por Produto")
        st.write("Visualize a ordem de prioridade dos fornecedores por produto")
        
        try:
            response = requests.get(
                f"{API_BASE}/fornecedores/ordem",
                headers=headers
            )
            
            if response.status_code == 200:
                ordens = response.json()
                
                # Buscar dados dos fornecedores
                response_forn = requests.get(
                    f"{API_BASE}/fornecedores",
                    headers=headers
                )
                
                if response_forn.status_code == 200:
                    fornecedores = response_forn.json()
                    id_to_fornecedor = {f['id']: f for f in fornecedores}
                    
                    if ordens:
                        for o in ordens:
                            with st.expander(f"{o['produto']} ({len(o.get('fornecedores_ids', []))} fornecedores)"):
                                if not o.get('fornecedores_ids'):
                                    st.write("Nenhum fornecedor para este produto.")
                                    continue
                                for idx, fid in enumerate(o['fornecedores_ids'], start=1):
                                    forn = id_to_fornecedor.get(fid)
                                    if forn:
                                        capacidade = None
                                        unidade = "kg"
                                        produto_info = None
                                        for p in forn.get('produtos', []):
                                            if p.get('nome', '').lower() == o['produto'].lower():
                                                produto_info = p
                                                capacidade = p.get('capacidade')
                                                unidade = p.get('unidade', 'kg')
                                                break
                                        cap_text = f"{capacidade} {unidade}" if capacidade is not None else "capacidade desconhecida"
                                        data_inscricao_produto = (produto_info or {}).get('data_inscricao') or forn.get('data_inscricao') or "N/D"
                                        local_flag = bool(forn.get('local', False))
                                        certificado_flag = bool(forn.get('certificado', False))
                                        biologico_flag = bool((produto_info or {}).get('biologico', False))

                                        st.markdown(
                                            f"{idx}. {forn['nome']} — {cap_text} | "
                                            f"📅 Inscrição produto: **{data_inscricao_produto}** | "
                                            f"📍 Local: **{'Sim' if local_flag else 'Não'}** | "
                                            f"✅ Certificado: **{'Sim' if certificado_flag else 'Não'}** | "
                                            f"🌿 Biológico: **{'Sim' if biologico_flag else 'Não'}**"
                                        )
                                    else:
                                        st.write(f"{idx}. {fid} — fornecedor não encontrado")
                    else:
                        st.info("Ainda não há ordens calculadas.")
                else:
                    st.error(f"❌ Erro ao carregar fornecedores: {response_forn.status_code}")
            else:
                st.error(f"❌ Erro ao carregar ordens: {response.status_code}")
        
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")


if __name__ == "__main__":
    # Para teste standalone
    st.session_state["role"] = "GESTOR_CANTINA"
    st.session_state["token"] = "test_token"
    mostrar_aprovisionamento()