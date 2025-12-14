import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

def list_fornecedores(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores", headers=headers)
    r.raise_for_status()
    return r.json()

def get_ordem(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores/ordem", headers=headers)
    r.raise_for_status()
    return r.json()

def get_preview_aprovisionamento(API_URL, auth_token, data_inicio, data_fim):
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"data_inicio": data_inicio, "data_fim": data_fim}
    r = requests.get(f"{API_URL}/aprovisionamento/preview", headers=headers, params=params)
    r.raise_for_status()
    return r.json()

def pagina_gestor_cantina(API_URL, auth_token):
    st.header("Gestão da Cantina")
    
    # Criar abas (4 abas reordenadas com emojis)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Previsão de Necessidades",
        "📋 Ordem de Fornecimento",
        "📊 Plano de Produção", 
        "⚠️ Alertas"
    ])
    
    # ============ TAB 1: PREVISÃO DE NECESSIDADES ============
    with tab1:
        st.subheader("🔍 Previsão de Necessidades")
        st.write("Gere uma previsão detalhada das necessidades de aprovisionamento")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio_prev = st.date_input(
                "Data Início",
                value=date.today(),
                key="tab1_preview_inicio"
            )
        with col2:
            data_fim_prev = st.date_input(
                "Data Fim",
                value=date.today() + timedelta(days=7),
                key="tab1_preview_fim"
            )
        
        if st.button("🔍 Ver Preview", key="tab1_btn_preview"):
            try:
                response = requests.get(
                    f"{API_URL}/aprovisionamento/preview",
                    params={
                        "data_inicio": str(data_inicio_prev),
                        "data_fim": str(data_fim_prev)
                    },
                    headers={"Authorization": f"Bearer {auth_token}"}
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
                            st.dataframe(df_planejadas, use_container_width=True)
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
                            use_container_width=True, 
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
                f"{API_URL}/fornecedores/ordem",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            if response.status_code == 200:
                ordens = response.json()
                
                # Buscar dados dos fornecedores
                response_forn = requests.get(
                    f"{API_URL}/fornecedores",
                    headers={"Authorization": f"Bearer {auth_token}"}
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
                                        for p in forn.get('produtos', []):
                                            if p.get('nome', '').lower() == o['produto'].lower():
                                                capacidade = p.get('capacidade')
                                                break
                                        cap_text = f"{capacidade} unidades" if capacidade is not None else "capacidade desconhecida"
                                        st.write(f"{idx}. {forn['nome']} — {cap_text}")
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
    
    # ============ TAB 3: PLANO DE PRODUÇÃO ============
    with tab3:
        st.subheader("Plano de Produção")
        st.write("Comparação entre previsão histórica e reservas reais")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(
                "Data Início",
                value=date.today(),
                key="tab3_plan_inicio"
            )
        with col2:
            data_fim = st.date_input(
                "Data Fim",
                value=date.today() + timedelta(days=6),
                key="tab3_plan_fim"
            )
        
        if st.button("📊 Ver Planejamento"):
            try:
                dados = get_preview_aprovisionamento(
                    API_URL, auth_token, 
                    data_inicio.isoformat(), 
                    data_fim.isoformat()
                )
                
                st.success(f"✅ Planejamento gerado para {dados['periodo']}")
                
                # Mostrar resumo das refeições
                if dados.get('refeicoes_detalhes'):
                    col_titulo, col_header_qtd = st.columns([3, 1])
                    with col_titulo:
                        st.markdown("<h3 style='text-align: center;'>Resumo das Refeições</h3>", unsafe_allow_html=True)
                    with col_header_qtd:
                        st.markdown("<h3 style='text-align: center;'>Produzir</h3>", unsafe_allow_html=True)
                    
                    for ref in dados['refeicoes_detalhes']:
                        # Calcula quantidade a produzir
                        qtd_produzir = ref.get('reservas_reais', 0)
                        if qtd_produzir == 0 and ref.get('previsao_reservas'):
                            qtd_produzir = ref['previsao_reservas']
                        
                        col_expander, col_qtd = st.columns([3, 1])
                        
                        with col_expander:
                            with st.expander(f"{ref['dia_nome']} ({ref['data']}) - {ref['tipo']}: {ref['descricao']}"):
                                st.write(f"**Dia da semana:** {ref['dia_semana_texto']}")
                                
                                # Previsão histórica
                                if ref.get('previsao_reservas'):
                                    st.write(f"**Previsão (histórico):** {ref['previsao_reservas']} refeições")
                                
                                # Reservas reais
                                if ref.get('reservas_reais') is not None:
                                    st.write(f"**Reservas reais:** {ref['reservas_reais']} refeições")
                                    
                                    # Comparação
                                    if ref.get('previsao_reservas'):
                                        dif = ref['reservas_reais'] - ref['previsao_reservas']
                                        perc = (dif / ref['previsao_reservas'] * 100) if ref['previsao_reservas'] > 0 else 0
                                        if abs(dif) > 0:
                                            st.write(f"**Diferença:** {dif:+.0f} ({perc:+.1f}%)")
                                else:
                                    st.info("Sem reservas reais ainda")
                                
                                # Ingredientes
                                if ref.get('ingredientes'):
                                    st.write("**Ingredientes:**")
                                    for ing in ref['ingredientes']:
                                        st.write(f"  • {ing['ingrediente']}: {ing['quantidade_estimada']} unidades")
                        
                        with col_qtd:
                            st.markdown(f"<div style='display: flex; align-items: center; justify-content: center; height: 48px; font-size: 20px; font-weight: bold;'>{qtd_produzir}</div>", unsafe_allow_html=True)
                
            except requests.exceptions.HTTPError as e:
                st.error(f"Erro ao gerar planejamento: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")
    
    # ============ TAB 4: ALERTAS ============
    with tab4:
        st.subheader("⚠️ Alertas de Desvio > 10%")
        st.write("Refeições com desvio significativo entre reservas reais e previsão histórica")
        
        try:
            # Buscar dados de todas as ementas disponíveis (últimos 30 dias até 30 dias futuros)
            data_inicio_alerta = date.today() - timedelta(days=30)
            data_fim_alerta = date.today() + timedelta(days=30)
            
            dados = get_preview_aprovisionamento(
                API_URL, auth_token,
                data_inicio_alerta.isoformat(),
                data_fim_alerta.isoformat()
            )
            
            # Calcular alertas a partir das refeições
            alertas = []
            for ref in dados.get('refeicoes_detalhes', []):
                previsao = ref.get('previsao_reservas') or 0
                real = ref.get('reservas_reais') or 0
                
                # Só calcular desvio se ambos os valores forem válidos e maiores que zero
                if previsao > 0 and real > 0:
                    desvio = ((real - previsao) / previsao) * 100
                    
                    if abs(desvio) > 10:
                        alertas.append({
                            "Data": ref['data'],
                            "Dia": ref['dia_nome'],
                            "Tipo": ref['tipo'].title(),
                            "Refeição": ref['descricao'],
                            "Previsão": previsao,
                            "Reservas Reais": real,
                            "Desvio (%)": f"{desvio:+.1f}%"
                        })
            
            if alertas:
                st.warning(f"⚠️ **{len(alertas)} alertas encontrados**")
                df_alertas = pd.DataFrame(alertas)
                st.dataframe(df_alertas, use_container_width=True)
            else:
                st.success("✅ Nenhum alerta de desvio > 10% encontrado")
        
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao carregar alertas: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"Erro: {str(e)}")
