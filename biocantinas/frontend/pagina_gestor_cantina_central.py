import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta, datetime

def list_fornecedores(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores", headers=headers)
    r.raise_for_status()
    return r.json()

def get_ordem(API_URL, auth_token, semana: int):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores/ordem", params={"semana": semana}, headers=headers)
    r.raise_for_status()
    return r.json()

def get_preview_aprovisionamento(API_URL, auth_token, data_inicio, data_fim):
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"data_inicio": data_inicio, "data_fim": data_fim}
    r = requests.get(f"{API_URL}/aprovisionamento/preview", headers=headers, params=params)
    r.raise_for_status()
    return r.json()


def patch_estado_fornecedor(API_URL, auth_token, fid, em_quarentena=None, freguesia=None):
    headers = {"Authorization": f"Bearer {auth_token}"}
    body = {}
    if em_quarentena is not None:
        body["em_quarentena"] = em_quarentena
    if freguesia is not None:
        body["freguesia"] = freguesia
    r = requests.patch(f"{API_URL}/fornecedores/{fid}/estado", json=body, headers=headers)
    r.raise_for_status()
    return r.json()


def list_fechos(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/freguesias/fechos", headers=headers)
    r.raise_for_status()
    return r.json()


def patch_fecho(API_URL, auth_token, nome: str, ativo: bool):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.patch(f"{API_URL}/freguesias/fechos", json={"nome": nome, "ativo": ativo}, headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_gestor_cantina_central(API_URL, auth_token):
    # Aumenta fonte das abas via CSS customizado
    st.markdown(
        """
        <style>
        .stTabs [data-baseweb="tab"] p {
            font-size: 24px !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.header("Gestão da Cantina Central - Aprovisionamento e Refeitórios")
    
    # Criar abas (6 abas com nova aba de Comparação)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Previsão de Necessidades",
        "📋 Ordem de Fornecimento",
        "📊 Plano de Produção", 
        "⚠️ Alertas",
        "✅ Registar Execuções",
        "📈 Comparação Realizado vs Previsto"
    ])
    
    # ============ TAB 1: PREVISÃO DE NECESSIDADES ============
    with tab1:
        st.subheader("🔍 Previsão de Necessidades")
        st.write("Selecione a semana do ano para gerar previsão de aprovisionamento")
        
        ano_corrente = date.today().year
        
        # Inicializar session_state
        if "preview_tab1_dados" not in st.session_state:
            st.session_state.preview_tab1_dados = None
        
        col1, col2 = st.columns([1, 3])
        with col1:
            semana_selecionada = st.number_input(
                "Semana do Ano",
                value=date.today().isocalendar()[1],
                min_value=1,
                max_value=52,
                key="tab1_semana"
            )
        
        # Calcular data início e fim a partir da semana
        if st.button("🔍 Ver Preview", key="tab1_btn_preview"):
            try:
                # Obter segunda-feira da semana
                jan4 = date(ano_corrente, 1, 4)
                week_one_monday = jan4 - timedelta(days=jan4.weekday())
                data_inicio_prev = week_one_monday + timedelta(weeks=int(semana_selecionada) - 1)
                data_fim_prev = data_inicio_prev + timedelta(days=6)
                
                response = requests.get(
                    f"{API_URL}/aprovisionamento/preview",
                    params={
                        "data_inicio": str(data_inicio_prev),
                        "data_fim": str(data_fim_prev)
                    },
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                
                if response.status_code == 200:
                    st.session_state.preview_tab1_dados = {
                        "dados": response.json(),
                        "semana": semana_selecionada,
                        "ano": ano_corrente,
                        "data_inicio": data_inicio_prev,
                        "data_fim": data_fim_prev
                    }
                else:
                    st.error(f"❌ Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
            
            except Exception as e:
                st.error(f"❌ Erro ao conectar com API: {str(e)}")
        
        # Mostrar dados se existem no session_state (FORA da condicional do botão)
        if st.session_state.preview_tab1_dados:
            preview_info = st.session_state.preview_tab1_dados
            dados = preview_info["dados"]
            semana_selecionada = preview_info["semana"]
            ano_corrente = preview_info["ano"]
            data_inicio_prev = preview_info["data_inicio"]
            data_fim_prev = preview_info["data_fim"]
            
            st.success(f"✅ Preview gerado para semana {semana_selecionada}/{ano_corrente}")
            st.info(f"📅 Período: {data_inicio_prev.strftime('%d/%m/%Y')} (Segunda) a {data_fim_prev.strftime('%d/%m/%Y')} (Domingo)")
            
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
                            unidade = ing.get('unidade_medida') or "kg"
                            quantidade = ing.get('quantidade_estimada', ing.get('quantidade', 0))
                            ementa_html += f"<li>{ing['ingrediente']}: {quantidade} {unidade}</li>"
                        ementa_html += "</ul><hr style='margin: 4px 0;'>"
                    ementa_html += "</div>"
                    st.markdown(ementa_html, unsafe_allow_html=True)
                else:
                    st.info("Sem ementas")
            
            with col2:
                st.markdown("**📊 Necessidades Planejadas**")
                st.caption("Quantidade total de produtos com histórico aplicado")
                
                if dados.get("necessidades_previstas_historico"):
                    necessidades_ajustadas = dados.get("necessidades_ajustadas", dados.get("necessidades_previstas_historico", {}))
                    necessidades_originais = dados.get("necessidades_previstas", {})
                    
                    df_planejadas = pd.DataFrame([
                        {
                            "Produto": prod,
                            "Quantidade Prevista (kg)": necessidades_originais.get(prod, qtd)
                        }
                        for prod, qtd in necessidades_ajustadas.items()
                    ])
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
    
    # ============ TAB 2: ORDEM DE FORNECIMENTO ============
    with tab2:
        st.subheader("📋 Ordem de Fornecimento por Produto")
        st.write("Visualize a ordem de prioridade dos fornecedores por produto")
        
        # Obter semana atual
        from datetime import date as date_class
        semana_atual = date_class.today().isocalendar()[1]
        
        try:
            response = requests.get(
                f"{API_URL}/fornecedores/ordem",
                params={"semana": int(semana_atual)},
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

                    # Freguesias em fecho
                    freguesias_fechadas = set()
                    try:
                        fechados = list_fechos(API_URL, auth_token)
                        freguesias_fechadas = {
                            (f.get("nome") or "").strip().lower()
                            for f in fechados
                            if f.get("ativo")
                        }
                    except Exception as e:
                        st.error(f"Erro ao carregar fechos: {e}")
                    
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

                                        estado_quarentena = forn.get('em_quarentena', False)
                                        freguesia_atual = forn.get('freguesia') or ""
                                        freguesia_fechada = (freguesia_atual.strip().lower() in freguesias_fechadas) if freguesia_atual else False

                                        data_inscricao_produto = (produto_info or {}).get('data_inscricao') or forn.get('data_inscricao') or "N/D"
                                        local_flag = bool(forn.get('local', False))
                                        certificado_flag = bool(forn.get('certificado', False))
                                        biologico_flag = bool((produto_info or {}).get('biologico', False))

                                        st.markdown(
                                            f"{idx}. {forn['nome']} — {cap_text}  | "
                                            f"🛡️ Quarentena: **{'Sim' if estado_quarentena else 'Não'}** | "
                                            f"📍 Freguesia: **{freguesia_atual or 'N/D'}**"
                                        )

                                        st.caption(
                                            f"📅 Inscrição produto: {data_inscricao_produto} | "
                                            f"🏠 Local: {'Sim' if local_flag else 'Não'} | "
                                            f"✅ Certificado: {'Sim' if certificado_flag else 'Não'} | "
                                            f"🌿 Biológico: {'Sim' if biologico_flag else 'Não'}"
                                        )

                                        if st.button(
                                            "Ativar quarentena" if not estado_quarentena else "Remover quarentena",
                                            key=f"qc_{fid}_{o['produto']}",
                                            type="secondary",
                                            help="Bloqueia todos os produtos deste fornecedor",
                                        ):
                                            patch_estado_fornecedor(API_URL, auth_token, fid, em_quarentena=not estado_quarentena)
                                            st.rerun()

                                        if freguesia_fechada:
                                            st.caption("Freguesia fechada — fornecedor não pode ser aprovado.")
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

        st.divider()
        st.subheader("🚫 Fechos sanitários por freguesia")

        try:
            fechados = list_fechos(API_URL, auth_token)
            fechados_ativos = [f for f in fechados if f.get("ativo")]
            if fechados_ativos:
                st.write("Freguesias bloqueadas:")
                for fecho in fechados_ativos:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"• {fecho['nome']}")
                    with col_b:
                        if st.button("Reabrir", key=f"reabrir_cantina_{fecho['nome']}"):
                            patch_fecho(API_URL, auth_token, fecho["nome"], False)
                            st.rerun()
            else:
                st.caption("Nenhuma freguesia em fecho sanitário.")

            FREGUESIAS_CINFAES = [
                "Alhões",
                "Bustelo",
                "Cinfães",
                "Espadanedo",
                "Ferreiros de Tendais",
                "Fornelos",
                "Freigil e Miomães",
                "Moimenta",
                "Nespereira",
                "Oliveira do Douro",
                "Santiago de Piães",
                "São Cristóvão de Nogueira",
                "Souselo",
                "Tarouquela",
                "Tendais",
                "Travanca",
            ]

            nova_freguesia = st.selectbox(
                "Selecionar freguesia para fecho",
                options=[""] + FREGUESIAS_CINFAES,
                key="nova_fecho_cantina",
                help="Ao fechar, todos os fornecedores dessa freguesia ficam reprovados automaticamente",
            )
            if st.button("Fechar freguesia", key="btn_fechar_freg_cantina"):
                if nova_freguesia.strip():
                    patch_fecho(API_URL, auth_token, nova_freguesia.strip(), True)
                    st.rerun()
                else:
                    st.error("Indique o nome da freguesia.")
        except requests.HTTPError as e:
            st.error(f"Erro ao gerir fechos: {e}")
    
    # ============ TAB 3: PLANO DE PRODUÇÃO ============
    with tab3:
        st.subheader("Plano de Produção")
        st.write("Comparação entre previsão histórica e reservas reais")
        
        ano_corrente_tab3 = date.today().year
        
        col1, col2 = st.columns([1, 3])
        with col1:
            semana_tab3 = st.number_input(
                "Semana do Ano",
                value=date.today().isocalendar()[1],
                min_value=1,
                max_value=52,
                key="tab3_semana"
            )
        
        if st.button("📊 Ver Planejamento"):
            try:
                # Calcular datas a partir da semana
                jan4 = date(ano_corrente_tab3, 1, 4)
                week_one_monday = jan4 - timedelta(days=jan4.weekday())
                data_inicio = week_one_monday + timedelta(weeks=int(semana_tab3) - 1)
                data_fim = data_inicio + timedelta(days=6)
                
                dados = get_preview_aprovisionamento(
                    API_URL, auth_token, 
                    data_inicio.isoformat(), 
                    data_fim.isoformat()
                )
                
                st.success(f"✅ Planejamento gerado para semana {semana_tab3}/{ano_corrente_tab3}")
                st.info(f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} (Segunda) a {data_fim.strftime('%d/%m/%Y')} (Domingo)")
                
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
                                        unidade = ing.get('unidade_medida') or "kg"
                                        st.write(f"  • {ing['ingrediente']}: {ing['quantidade_estimada']} {unidade}")
                        
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
                st.dataframe(df_alertas, width='stretch')
            else:
                st.success("✅ Nenhum alerta de desvio > 10% encontrado")
        
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao carregar alertas: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"Erro: {str(e)}")
    
    # ============ TAB 5: REGISTAR EXECUÇÕES ============
    with tab5:
        st.subheader("✅ Registar Execução de Refeições")
        st.write("Registe quantas refeições foram servidas e não servidas. A quantidade produzida vem da previsão do plano de produção.")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Listar ementas
        try:
            resp_ementas = requests.get(f"{API_URL}/ementas", headers=headers)
            if resp_ementas.status_code == 200:
                ementas = resp_ementas.json()
                
                if ementas:
                    # Seletor de ementa
                    ementa_options = {f"{e['nome']} ({e['data_inicio']} a {e['data_fim']})": e for e in ementas}
                    selected_ementa_label = st.selectbox("Selecionar Ementa", list(ementa_options.keys()), key="exec_ementa")
                    selected_ementa = ementa_options[selected_ementa_label]
                    
                    st.info(f"📅 Período: {selected_ementa['data_inicio']} a {selected_ementa['data_fim']}")
                    
                    # Buscar previsões do plano de produção
                    try:
                        data_inicio_ementa = selected_ementa['data_inicio']
                        data_fim_ementa = selected_ementa['data_fim']
                        
                        resp_preview = requests.get(
                            f"{API_URL}/aprovisionamento/preview",
                            params={"data_inicio": data_inicio_ementa, "data_fim": data_fim_ementa},
                            headers=headers
                        )
                        
                        previsoes_por_refeicao = {}
                        if resp_preview.status_code == 200:
                            preview_data = resp_preview.json()
                            for ref in preview_data.get('refeicoes_detalhes', []):
                                # Chave: (data, tipo)
                                chave = (ref['data'], ref['tipo'])
                                previsoes_por_refeicao[chave] = ref.get('previsao_reservas') or 0
                    except Exception as e:
                        st.warning(f"Não foi possível carregar previsões: {e}")
                        previsoes_por_refeicao = {}
                    
                    # Listar refeições da ementa
                    dias_nome = {1: "Segunda", 2: "Terça", 3: "Quarta", 4: "Quinta", 5: "Sexta"}
                    refeicoes_agrupadas = {}
                    
                    for refeicao in selected_ementa.get('refeicoes', []):
                        dia_key = (refeicao['dia_semana'], dias_nome.get(refeicao['dia_semana'], f"Dia {refeicao['dia_semana']}"))
                        if dia_key not in refeicoes_agrupadas:
                            refeicoes_agrupadas[dia_key] = []
                        refeicoes_agrupadas[dia_key].append(refeicao)
                    
                    # Formulário por dia
                    for (dia_num, dia_label), refeicoes_dia in sorted(refeicoes_agrupadas.items()):
                        with st.expander(f"📅 {dia_label} (Dia {dia_num})"):
                            for refeicao in refeicoes_dia:
                                st.markdown(f"**{refeicao['tipo'].title()}: {refeicao.get('descricao', 'Sem descrição')}**")
                                
                                # Calcular data da refeição baseada no dia da semana
                                data_inicio_obj = datetime.strptime(selected_ementa['data_inicio'], '%Y-%m-%d').date()
                                data_refeicao = data_inicio_obj
                                while (data_refeicao.weekday() + 1) != dia_num:
                                    data_refeicao += timedelta(days=1)
                                    if data_refeicao > datetime.strptime(selected_ementa['data_fim'], '%Y-%m-%d').date():
                                        data_refeicao = data_inicio_obj
                                        break
                                
                                # Buscar previsão
                                chave_previsao = (str(data_refeicao), refeicao['tipo'])
                                qty_prevista = previsoes_por_refeicao.get(chave_previsao, 0)
                                
                                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                                
                                with col1:
                                    data_execucao = st.date_input(
                                        "Data da Execução",
                                        value=data_refeicao,
                                        key=f"data_exec_{refeicao['id']}"
                                    )
                                
                                with col2:
                                    qty_prod = st.number_input(
                                        "Produzido (previsão)",
                                        min_value=0,
                                        value=int(qty_prevista) if qty_prevista else 0,
                                        key=f"prod_{refeicao['id']}",
                                        help="Quantidade prevista pelo plano de produção"
                                    )
                                
                                with col3:
                                    qty_serv = st.number_input(
                                        "Servido",
                                        min_value=0,
                                        value=0,
                                        max_value=qty_prod,
                                        key=f"serv_{refeicao['id']}"
                                    )
                                
                                with col4:
                                    qty_nao_serv = st.number_input(
                                        "Não Servido",
                                        min_value=0,
                                        value=0,
                                        max_value=qty_prod,
                                        key=f"nao_serv_{refeicao['id']}"
                                    )
                                
                                # Validação em tempo real
                                if qty_serv + qty_nao_serv != qty_prod:
                                    st.warning(f"⚠️ Servido ({qty_serv}) + Não Servido ({qty_nao_serv}) = {qty_serv + qty_nao_serv}, deve ser igual a Produzido ({qty_prod})")
                                
                                if st.button(f"💾 Registar", key=f"btn_exec_{refeicao['id']}", disabled=(qty_serv + qty_nao_serv != qty_prod)):
                                    if qty_prod <= 0:
                                        st.error("Quantidade produzida deve ser maior que 0")
                                    else:
                                        try:
                                            payload = {
                                                "refeicao_id": refeicao['id'],
                                                "data_execucao": str(data_execucao),
                                                "quantidade_prevista": int(qty_prevista) if qty_prevista else None,
                                                "quantidade_produzida": qty_prod,
                                                "quantidade_servida": qty_serv,
                                                "quantidade_nao_servida": qty_nao_serv
                                            }
                                            
                                            resp = requests.post(
                                                f"{API_URL}/execucaoRefeicao/",
                                                json=payload,
                                                headers=headers
                                            )
                                            
                                            if resp.status_code == 200:
                                                st.success("✅ Execução registada com sucesso!")
                                                st.rerun()
                                            else:
                                                st.error(f"Erro: {resp.status_code} - {resp.json().get('detail', 'Erro desconhecido')}")
                                        except Exception as e:
                                            st.error(f"Erro ao registar: {e}")
                                
                                st.divider()
                    
                    # Histórico de execuções
                    st.markdown("### 📋 Histórico de Execuções")
                    data_inicio_ementa = selected_ementa['data_inicio']
                    data_fim_ementa = selected_ementa['data_fim']
                    
                    try:
                        resp_hist = requests.get(
                            f"{API_URL}/execucaoRefeicao/",
                            params={"data_inicio": data_inicio_ementa, "data_fim": data_fim_ementa},
                            headers=headers
                        )
                        
                        if resp_hist.status_code == 200:
                            execucoes = resp_hist.json()
                            
                            if execucoes:
                                df_exec = pd.DataFrame([
                                    {
                                        "Data": e['data_execucao'],
                                        "Refeição ID": e['refeicao_id'],
                                        "Previsto": e.get('quantidade_prevista', '-'),
                                        "Produzido": e['quantidade_produzida'],
                                        "Servido": e['quantidade_servida'],
                                        "Não Servido": e['quantidade_nao_servida'],
                                        "% Desperdício": f"{(e['quantidade_nao_servida'] / e['quantidade_produzida'] * 100):.1f}%" if e['quantidade_produzida'] > 0 else "0%",
                                        "Desvio Previsão": f"{(e['quantidade_produzida'] - e.get('quantidade_prevista', e['quantidade_produzida'])):+d}" if e.get('quantidade_prevista') else "-"
                                    }
                                    for e in execucoes
                                ])
                                st.dataframe(df_exec, use_container_width=True, hide_index=True)
                            else:
                                st.info("Ainda não há execuções registadas para esta ementa")
                        else:
                            st.error("Erro ao carregar histórico")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.info("Ainda não há ementas cadastradas")
            else:
                st.error("Erro ao carregar ementas")
        except Exception as e:
            st.error(f"Erro: {e}")

    # ============ TAB 6: COMPARAÇÃO REALIZADO VS PREVISTO ============
    with tab6:
        st.subheader("📈 Comparação: Realizado vs Previsto")
        st.write("Analise a execução real em relação ao plano de produção")
        
        # Seletor de período
        col1, col2 = st.columns(2)
        with col1:
            data_inicio_relatorio = st.date_input("Data início", value=date.today() - timedelta(days=7))
        with col2:
            data_fim_relatorio = st.date_input("Data fim", value=date.today())
        
        # Botão para gerar relatório
        if st.button("📊 Gerar Relatório"):
            try:
                headers = {"Authorization": f"Bearer {auth_token}"}
                
                response = requests.get(
                    f"{API_URL}/relatorios/comparacao-execucao",
                    params={
                        "data_inicio": str(data_inicio_relatorio),
                        "data_fim": str(data_fim_relatorio)
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    relatorio = response.json()
                    st.session_state.relatorio_gerado = relatorio
                else:
                    st.error(f"❌ Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
            except Exception as e:
                st.error(f"❌ Erro ao conectar com API: {str(e)}")
        
        # Exibir relatório se existe
        if "relatorio_gerado" in st.session_state:
            relatorio = st.session_state.relatorio_gerado
            
            st.divider()
            
            # Resumo geral
            col1, col2, col3, col4 = st.columns(4)
            resumo = relatorio.get("resumo", {})
            
            with col1:
                st.metric(
                    "Produtos Analisados",
                    resumo.get("produtos_analisados", 0)
                )
            with col2:
                st.metric(
                    "⬆️ Excesso",
                    resumo.get("desvios_positivos", 0)
                )
            with col3:
                st.metric(
                    "⬇️ Falta",
                    resumo.get("desvios_negativos", 0)
                )
            with col4:
                st.metric(
                    "🚨 Alertas",
                    resumo.get("desvios_alerta", 0)
                )
            
            st.divider()
            
            # Tabela de detalhes
            st.markdown("### Detalhes por Produto")
            
            if relatorio.get("detalhes"):
                df_detalhes = pd.DataFrame(relatorio.get("detalhes", []))
                
                # Formatar a tabela
                st.dataframe(
                    df_detalhes.style.apply(
                        lambda row: [
                            'background-color: #ff9999' if row['requer_alerta'] and row['status'] == '⬆️ Excesso' else
                            'background-color: #ffcc99' if row['requer_alerta'] and row['status'] == '⬇️ Falta' else
                            'background-color: #99ff99' if not row['requer_alerta'] else ''
                            for _ in row
                        ],
                        axis=1
                    ),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Análise por status
                st.markdown("### 📊 Análise de Desvios")
                
                df_alertas = df_detalhes[df_detalhes['requer_alerta'] == True]
                
                if len(df_alertas) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### ⬆️ Produtos com Excesso (>10%)")
                        excesso = df_alertas[df_alertas['status'] == '⬆️ Excesso']
                        if len(excesso) > 0:
                            for _, row in excesso.iterrows():
                                st.warning(
                                    f"**{row['produto']}**: +{row['desvio_percentual']}% "
                                    f"({row['quantidade_realizada']} vs {row['quantidade_prevista']} previsto)"
                                )
                        else:
                            st.info("Nenhum produto com excesso")
                    
                    with col2:
                        st.markdown("#### ⬇️ Produtos com Falta (>10%)")
                        falta = df_alertas[df_alertas['status'] == '⬇️ Falta']
                        if len(falta) > 0:
                            for _, row in falta.iterrows():
                                st.warning(
                                    f"**{row['produto']}**: {row['desvio_percentual']}% "
                                    f"({row['quantidade_realizada']} vs {row['quantidade_prevista']} previsto)"
                                )
                        else:
                            st.info("Nenhum produto com falta")
                else:
                    st.success("✅ Nenhum desvio significativo detectado!")
                
                # Botão para atualizar plano com consumo real
                st.divider()
                if st.button("💾 Atualizar Plano com Consumo Real"):
                    try:
                        resp_update = requests.post(
                            f"{API_URL}/relatorios/atualizar-consumo-realizado",
                            params={
                                "data_inicio": str(data_inicio_relatorio),
                                "data_fim": str(data_fim_relatorio)
                            },
                            headers=headers
                        )
                        
                        if resp_update.status_code == 200:
                            st.success("✅ Plano atualizado com consumo realizado!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {resp_update.json().get('detail', 'Erro desconhecido')}")
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")
            else:
                st.info("Sem dados de comparação para o período selecionado")

