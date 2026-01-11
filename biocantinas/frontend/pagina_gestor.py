import streamlit as st
import requests
import json
import html

def list_fornecedores(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores", headers=headers)
    r.raise_for_status()
    return r.json()

def patch_aprovacao(API_URL, auth_token, fid, aprovado: bool):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.patch(
        f"{API_URL}/fornecedores/{fid}/aprovacao",
        json={"aprovado": aprovado},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()

def get_ordem(API_URL, auth_token, semana: int):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores/ordem", params={"semana": semana}, headers=headers)
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

def get_ementas(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/ementas", headers=headers)
    r.raise_for_status()
    return r.json()

def get_kpi_ementa(API_URL, auth_token, ementa_id):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/kpi/ementa/{ementa_id}", headers=headers)
    r.raise_for_status()
    return r.json()

def get_desperdicio_ementa(API_URL, auth_token, ementa_id):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/kpi/desperdicio/ementa/{ementa_id}", headers=headers)
    r.raise_for_status()
    return r.json()

def get_kpi_consolidado(API_URL, auth_token, ementa_id):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/kpi/consolidado/{ementa_id}", headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_gestor(API_URL, auth_token):
    st.header("Gestão de Fornecedores")

    # Criar abas
    tab1, tab2, tab3 = st.tabs(["Fornecedores", "Ordem de Fornecimento", "KPIs - Sustentabilidade"])
    
    # Aba 1: Fornecedores
    with tab1:
        if st.button("Recarregar lista"):
            st.rerun()

        fornecedores = list_fornecedores(API_URL, auth_token)

        # Carregar freguesias em fecho para bloquear aprovação
        fechados_data = []
        freguesias_fechadas = set()
        try:
            fechados_data = list_fechos(API_URL, auth_token)
            freguesias_fechadas = {
                (f.get("nome") or "").strip().lower()
                for f in fechados_data
                if f.get("ativo")
            }
        except requests.HTTPError as e:
            st.error(f"Erro ao carregar fechos: {e}")

        if fornecedores:
            st.subheader("Lista de Fornecedores")
            for f in fornecedores:
                col1, col2, col3 = st.columns([5, 1, 1])
                
                with col1:
                    with st.expander(f"#{f['id']} - {f['nome']}"):
                        st.caption(
                            f"Data inscrição: {f['data_inscricao']} | "
                            f"Aprovado: {f['aprovado']}"
                        )

                        estado_quarentena = f.get('em_quarentena', False)
                        freguesia_atual = f.get('freguesia') or ""
                        freguesia_fechada = (freguesia_atual.strip().lower() in freguesias_fechadas) if freguesia_atual else False
                        st.markdown(
                            f"🛡️ Quarentena: **{'Sim' if estado_quarentena else 'Não'}** | "
                            f"📍 Freguesia: **{freguesia_atual or 'N/D'}**"
                        )

                        cols_estado = st.columns([1])
                        with cols_estado[0]:
                            if st.button(
                                "Ativar quarentena" if not estado_quarentena else "Remover quarentena",
                                key=f"q_{f['id']}",
                                type="secondary",
                                help="Bloqueia todos os produtos deste fornecedor",
                            ):
                                patch_estado_fornecedor(API_URL, auth_token, f["id"], em_quarentena=not estado_quarentena)
                                st.rerun()
                        
                        # Listar produtos
                        produtos = f.get('produtos', [])
                        if produtos:
                            st.write("**Produtos:**")
                            for p in produtos:
                                unidade = p.get('unidade', 'kg')
                                st.write(f"  • {p['nome']} ({p.get('tipo', 'N/A')}) - Capacidade: {p.get('capacidade', 'N/A')} {unidade}")

                                cert = p.get('certificado')
                                if cert:
                                    texto_cert = None
                                    arquivo_url = None
                                    arquivo_nome = None
                                    try:
                                        cert_obj = json.loads(cert)
                                        texto_cert = cert_obj.get("texto")
                                        arquivo_url = cert_obj.get("arquivo_url")
                                        arquivo_nome = cert_obj.get("arquivo_nome")
                                    except Exception:
                                        texto_cert = cert
                                    partes_html = []
                                    if texto_cert:
                                        partes_html.append(html.escape(texto_cert))
                                    if arquivo_url:
                                        resolved_url = arquivo_url if str(arquivo_url).startswith("http") else f"{API_URL}{arquivo_url}"
                                        link_label = html.escape(arquivo_nome or "Ver certificado")
                                        partes_html.append(f"<a href='{resolved_url}' target='_blank' rel='noopener noreferrer'>{link_label}</a>")
                                    conteudo_cert = "<br>".join(partes_html) if partes_html else html.escape(str(cert))
                                    st.markdown(
                                        f"<div style='margin-left:12px;'>📜 Certificado:<br><div style='background: #f7f7f9; padding: 6px; border-radius: 6px;'>{conteudo_cert}</div></div>",
                                        unsafe_allow_html=True,
                                    )
                        else:
                            st.write("Sem produtos cadastrados")
                
                with col2:
                    if not f["aprovado"]:
                        if estado_quarentena:
                            st.caption("Não é possível aprovar enquanto estiver em quarentena.")
                        elif freguesia_fechada:
                            st.caption("Não é possível aprovar enquanto a freguesia estiver fechada.")
                        else:
                            if st.button("Aprovar", key=f"ap_{f['id']}"):
                                patch_aprovacao(API_URL, auth_token, f["id"], True)
                                st.rerun()
                
                with col3:
                    if f["aprovado"]:
                        if st.button("Reprovar", key=f"rp_{f['id']}"):
                            patch_aprovacao(API_URL, auth_token, f["id"], False)
                            st.rerun()
        else:
            st.info("Ainda não há fornecedores.")

        st.divider()
        st.subheader("🚫 Fechos sanitários por freguesia")

        try:
            fechados = fechados_data or list_fechos(API_URL, auth_token)
            fechados_ativos = [f for f in fechados if f.get("ativo")]
            if fechados_ativos:
                st.write("Freguesias bloqueadas:")
                for fecho in fechados_ativos:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"• {fecho['nome']}")
                    with col_b:
                        if st.button("Reabrir", key=f"reabrir_{fecho['nome']}"):
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
                key="nova_fecho",
                help="Ao fechar, todos os fornecedores dessa freguesia ficam reprovados automaticamente",
            )
            if st.button("Fechar freguesia", key="btn_fechar_freg"):
                if nova_freguesia.strip():
                    patch_fecho(API_URL, auth_token, nova_freguesia.strip(), True)
                    st.rerun()
                else:
                    st.error("Indique o nome da freguesia.")
        except requests.HTTPError as e:
            st.error(f"Erro ao gerir fechos: {e}")
    
    # Aba 2: Ordem de Fornecimento
    with tab2:
        st.subheader("Ordem de fornecimento por produto")
        
        # Obter semana atual
        from datetime import date as date_class
        semana_atual = date_class.today().isocalendar()[1]

        try:
            fornecedores = list_fornecedores(API_URL, auth_token)
            ordens = get_ordem(API_URL, auth_token, semana_atual)
            
            if ordens:
                # mapa id -> fornecedor para apresentar nomes e capacidades
                id_to_fornecedor = {f['id']: f for f in fornecedores}
                
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
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao carregar ordem: {e.response.status_code} - {e.response.text}")
    
    # Aba 3: KPIs - Sustentabilidade
    with tab3:
        st.subheader("📊 KPIs - Sustentabilidade & Desperdício")
        
        try:
            ementas = get_ementas(API_URL, auth_token)
            
            if not ementas:
                st.info("Ainda não há ementas cadastradas.")
            else:
                # Seletor de ementa
                ementa_options = {f"{e['nome']} ({e['data_inicio']} a {e['data_fim']})": e['id'] for e in ementas}
                selected_ementa_label = st.selectbox("Selecionar Ementa", list(ementa_options.keys()))
                selected_ementa_id = ementa_options[selected_ementa_label]
                
                # Subtabs para KPIs
                # KPIs alinhados aos requisitos: % biológicos e desperdício (servido vs não servido)
                kpi_tab1, kpi_tab2, kpi_tab3 = st.tabs(["Consolidado", "Sustentabilidade", "Desperdício"])
                
                # TAB CONSOLIDADO
                with kpi_tab1:
                    if st.button("Calcular KPIs Consolidados", type="primary", key="calc_consolidado"):
                        with st.spinner("Calculando KPIs consolidados..."):
                            try:
                                kpi_consol = get_kpi_consolidado(API_URL, auth_token, selected_ementa_id)
                                
                                st.markdown(f"### 📈 {kpi_consol['ementa_nome']}")
                                
                                # Métricas principais
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric(
                                        "🌿 % Biológico",
                                        f"{kpi_consol['percentagem_biologica']:.1f}%",
                                        help="Percentagem de ingredientes biológicos usados nas receitas desta ementa"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "♻️ % Desperdício",
                                        f"{kpi_consol['taxa_desperdicio']:.1f}%",
                                        help="Percentagem de refeições produzidas que não foram servidas"
                                    )
                                
                                with col3:
                                    st.metric(
                                        "✅ % Servido",
                                        f"{kpi_consol['taxa_servida']:.1f}%",
                                        help="Percentagem de refeições servidas face ao produzido"
                                    )
                                
                                with col4:
                                    total = kpi_consol['total_produzido']
                                    st.metric(
                                        "📊 Total Produzido",
                                        f"{total}"
                                    )
                                
                                # Detalhes de produção
                                st.markdown("---")
                                st.markdown("#### 📦 Resumo de Produção")
                                
                                col_prod, col_serv, col_desp = st.columns(3)
                                
                                with col_prod:
                                    st.info(f"**Produzido**\n{kpi_consol['total_produzido']} unidades")
                                
                                with col_serv:
                                    st.success(f"**Servido**\n{kpi_consol['total_servido']} unidades ({kpi_consol['taxa_servida']:.1f}%)")
                                
                                with col_desp:
                                    st.warning(f"**Não Servido**\n{kpi_consol['total_nao_servido']} unidades ({kpi_consol['taxa_desperdicio']:.1f}%)")
                                
                                # Recomendações consolidadas
                                st.markdown("---")
                                st.markdown("#### 💡 Recomendações Estratégicas")
                                
                                recomendacoes = []
                                
                                if kpi_consol['percentagem_biologica'] >= 80:
                                    recomendacoes.append("✅ Excelente utilização de produtos biológicos!")
                                elif kpi_consol['percentagem_biologica'] >= 50:
                                    recomendacoes.append("⚠️ Aumentar fornecedores de produtos biológicos")
                                else:
                                    recomendacoes.append("❌ Prioridade: expandir rede de fornecedores biológicos")
                                
                                if kpi_consol['taxa_desperdicio'] <= 15:
                                    recomendacoes.append("✅ Excelente controlo de desperdício!")
                                elif kpi_consol['taxa_desperdicio'] <= 25:
                                    recomendacoes.append("⚠️ Revisar planeamento de produção")
                                else:
                                    recomendacoes.append("❌ Ação urgente: reduzir desperdício significativamente")
                                
                                for rec in recomendacoes:
                                    st.write(f"• {rec}")
                                
                            except Exception as e:
                                st.error(f"Erro ao calcular: {str(e)}")
                
                # TAB SUSTENTABILIDADE
                with kpi_tab2:
                    st.markdown("Percentagem de produtos biológicos utilizados nas ementas (por dia e por refeição)")
                    
                    if st.button("Calcular Sustentabilidade", key="calc_sustent"):
                        with st.spinner("Calculando KPI de sustentabilidade..."):
                            try:
                                kpi_data = get_kpi_ementa(API_URL, auth_token, selected_ementa_id)
                                
                                st.markdown(f"### 🌿 {kpi_data['ementa_nome']}")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric(
                                        "Média Semanal", 
                                        f"{kpi_data['media_percentagem_biologica']:.1f}%",
                                        help="Percentagem média de produtos biológicos"
                                    )
                                with col2:
                                    status = "✅ Excelente" if kpi_data['media_percentagem_biologica'] >= 80 else "⚠️ Melhorar" if kpi_data['media_percentagem_biologica'] >= 50 else "❌ Crítico"
                                    st.metric("Status", status)
                                with col3:
                                    total_dias = len(kpi_data['dias'])
                                    st.metric("Dias analisados", total_dias)
                                
                                st.markdown("---")
                                st.markdown("#### 📅 Detalhamento por Dia (Almoço vs Jantar)")
                                
                                dias_nome = {1: "Segunda-feira", 2: "Terça-feira", 3: "Quarta-feira", 4: "Quinta-feira", 5: "Sexta-feira"}
                                
                                for dia in kpi_data['dias']:
                                    dia_nome = dias_nome.get(dia['dia_semana'], f"Dia {dia['dia_semana']}")
                                    with st.expander(f"{dia_nome} - Média: {dia['media_percentagem_biologica']:.1f}%"):
                                        col_a, col_b = st.columns(2)
                                        
                                        with col_a:
                                            st.markdown("**🍽️ Almoço**")
                                            st.progress(min(dia['percentagem_biologica_almoco'] / 100, 1.0))
                                            st.write(f"{dia['percentagem_biologica_almoco']:.1f}% biológico")

                                        with col_b:
                                            st.markdown("**🌙 Jantar**")
                                            st.progress(min(dia['percentagem_biologica_jantar'] / 100, 1.0))
                                            st.write(f"{dia['percentagem_biologica_jantar']:.1f}% biológico")
                                
                                st.markdown("---")
                                st.markdown("#### 📊 Gráfico Semanal")
                                
                                if kpi_data['dias']:
                                    import pandas as pd
                                    chart_data = pd.DataFrame([
                                        {
                                            "Dia": dias_nome.get(dia['dia_semana'], f"Dia {dia['dia_semana']}"),
                                            "Almoço": dia['percentagem_biologica_almoco'],
                                            "Jantar": dia['percentagem_biologica_jantar']
                                        }
                                        for dia in kpi_data['dias']
                                    ])
                                    
                                    st.bar_chart(chart_data.set_index("Dia"), height=400)
                                else:
                                    st.info("Não há dados de dias para exibir no gráfico. Verifique se a ementa tem refeições cadastradas.")
                                
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")
                
                # TAB DESPERDÍCIO
                with kpi_tab3:
                    st.markdown("Taxa de desperdício (% não servido) e refeições servidas por dia")
                    
                    if st.button("Calcular Desperdício", key="calc_desp"):
                        with st.spinner("Calculando KPI de desperdício..."):
                            try:
                                kpi_desp = get_desperdicio_ementa(API_URL, auth_token, selected_ementa_id)
                                
                                st.markdown(f"### ♻️ {kpi_desp['ementa_nome']}")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric(
                                        "Total Produzido",
                                        f"{kpi_desp['total_produzido']}",
                                        help="Quantidade total de refeições produzidas"
                                    )
                                with col2:
                                    st.metric(
                                        "Total Servido",
                                        f"{kpi_desp['total_servido']}",
                                        help="Quantidade total de refeições servidas"
                                    )
                                with col3:
                                    st.metric(
                                        "Não Servido",
                                        f"{kpi_desp['total_nao_servido']}",
                                        help="Quantidade produzida que não foi servida"
                                    )
                                with col4:
                                    st.metric(
                                        "Taxa Desperdício (% não servido)",
                                        f"{kpi_desp['taxa_desperdicio_geral']:.1f}%",
                                        help="Percentagem de refeições não servidas sobre o total produzido"
                                    )
                                
                                st.markdown("---")
                                st.markdown("#### 📅 Desperdício por Dia")
                                
                                dias_nome = {1: "Segunda", 2: "Terça", 3: "Quarta", 4: "Quinta", 5: "Sexta"}
                                
                                for dia in kpi_desp['dias']:
                                    with st.expander(f"{dias_nome.get(dia['dia_semana'])} - Desperdício: {dia['taxa_desperdicio_media']:.1f}% (não servido)"):
                                        col_a, col_b, col_c = st.columns(3)
                                        
                                        with col_a:
                                            st.write(f"**Produzido:** {dia['total_produzido']}")
                                        with col_b:
                                            st.write(f"**Servido:** {dia['total_servido']} ({dia['taxa_servida_media']:.1f}%)")
                                        with col_c:
                                            st.write(f"**Desperdiçado:** {dia['total_nao_servido']} ({dia['taxa_desperdicio_media']:.1f}%)")
                                        
                                        st.progress(min(dia['taxa_desperdicio_media'] / 100, 1.0))
                                
                                st.markdown("---")
                                st.markdown("#### 📊 Gráfico de Desperdício")
                                
                                if kpi_desp['dias']:
                                    import pandas as pd
                                    chart_data = pd.DataFrame([
                                        {
                                            "Dia": dias_nome.get(dia['dia_semana']),
                                            "Servido": dia['taxa_servida_media'],
                                            "Desperdiçado": dia['taxa_desperdicio_media']
                                        }
                                        for dia in kpi_desp['dias']
                                    ])
                                    
                                    st.bar_chart(chart_data.set_index("Dia"), height=400)
                                else:
                                    st.info("Não há dados de desperdício. Verifique se há execuções de refeições registadas.")
                                
                                # Alertas
                                st.markdown("---")
                                st.markdown("#### ⚠️ Alertas")
                                
                                if kpi_desp['taxa_desperdicio_geral'] <= 15:
                                    st.success(f"✅ Excelente! Desperdício controlado ({kpi_desp['taxa_desperdicio_geral']:.1f}%)")
                                elif kpi_desp['taxa_desperdicio_geral'] <= 25:
                                    st.warning(f"⚠️ Atenção: Desperdício acima do ideal ({kpi_desp['taxa_desperdicio_geral']:.1f}%)")
                                else:
                                    st.error(f"❌ Crítico: Desperdício muito elevado ({kpi_desp['taxa_desperdicio_geral']:.1f}%)")
                                
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")
                
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao carregar KPIs: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"Erro inesperado: {str(e)}")
