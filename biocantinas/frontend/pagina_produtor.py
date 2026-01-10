
import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd

def create_fornecedor(API_URL, auth_token, payload):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.post(f"{API_URL}/fornecedores", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_produtor(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Carregar catálogo de produtos
    try:
        cat_resp = requests.get(f"{API_URL}/produtos-catalogo/")
        cat_resp.raise_for_status()
        catalogo = cat_resp.json()
    except Exception:
        catalogo = []
    catalogo_por_id = {p.get("id"): p for p in catalogo}
    
    # Obter informações do fornecedor para o título
    try:
        perfil_response = requests.get(
            f"{API_URL}/fornecedores/meu-perfil",
            headers=headers
        )
        if perfil_response.status_code == 200:
            perfil = perfil_response.json()
            nome_fornecedor = perfil.get("nome", "Produtor")
            st.header(f"Bem vindo, {nome_fornecedor}")
        else:
            st.header("Área do Produtor")
    except:
        st.header("Área do Produtor")
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs([
        "📋 Minhas Informações",
        "🔍 Previsão de Fornecimento",
        "📝 Registro de Produtos"
    ])
    
    # ============ TAB 1: MINHAS INFORMAÇÕES ============
    with tab1:
        try:
            perfil_response = requests.get(
                f"{API_URL}/fornecedores/meu-perfil",
                headers=headers
            )
            
            if perfil_response.status_code == 200:
                perfil = perfil_response.json()
                
                # Mostrar nome, status e data de inscrição
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Nome Registado", perfil.get("nome", "N/A"))
                with col2:
                    # Determinar status correto: se não é local, é reprovado
                    if not perfil.get("local", False):
                        status_text = "❌ Reprovado (Não Local)"
                    elif perfil.get("aprovado"):
                        status_text = "✅ Aprovado"
                    else:
                        status_text = "⏳ Pendente"
                    st.metric("Status", status_text)
                with col3:
                    data_inscricao = perfil.get("data_inscricao", "N/A")
                    st.metric("Data de Inscrição", data_inscricao)
                with col4:
                    local_status = "✅ Sim" if perfil.get("local", False) else "❌ Não"
                    st.metric("Produtor Local", local_status)
                with col5:
                    cert_status = "✅ Sim" if perfil.get("certificado", False) else "❌ Não"
                    st.metric("Certificado Agrícola", cert_status)
                
                st.divider()
                
                # Mostrar aviso se não é local
                if not perfil.get("local", False):
                    st.error("❌ **Atenção:** Apenas produtores locais podem ser aprovados.")
                
                produtos = perfil.get("produtos", [])
                
                if produtos:
                    # Tabela de produtos
                    st.markdown("### 🌱 Produtos Cadastrados")
                    
                    # Calcular prioridades
                    try:
                        ordem_response = requests.get(
                            f"{API_URL}/fornecedores/ordem",
                            headers=headers
                        )
                        ordem_data = ordem_response.json() if ordem_response.status_code == 200 else []
                    except:
                        ordem_data = []
                    
                    produtos_info = []
                    for produto in produtos:
                        # Encontrar prioridade
                        prioridade = None
                        nome_cat = catalogo_por_id.get(produto.get("produto_id"), {}).get("nome", "")
                        tipo_cat = catalogo_por_id.get(produto.get("produto_id"), {}).get("tipo", "N/A")
                        unidade_medida = catalogo_por_id.get(produto.get("produto_id"), {}).get("unidade_medida", "kg")
                        
                        for ordem_item in ordem_data:
                            if ordem_item["produto"].lower() == nome_cat.lower():
                                fornecedores_ids = ordem_item.get("fornecedores_ids", [])
                                if perfil["id"] in fornecedores_ids:
                                    prioridade = fornecedores_ids.index(perfil["id"]) + 1
                                break
                        
                        # Formatar capacidade com unidade de medida
                        capacidade = produto.get("capacidade", 0)
                        capacidade_texto = f"{capacidade} {unidade_medida}" if unidade_medida else str(capacidade)
                        
                        produtos_info.append({
                            "Produto": nome_cat,
                            "Tipo": tipo_cat,
                            "Capacidade": capacidade_texto,
                            "Início Produção": produto.get("intervalo_producao_inicio", "N/A"),
                            "Fim Produção": produto.get("intervalo_producao_fim", "N/A"),
                            "Prioridade": prioridade if prioridade else "N/A"
                        })
                    
                    df_produtos = pd.DataFrame(produtos_info)
                    st.dataframe(df_produtos, use_container_width=True, hide_index=True)
                    
                else:
                    st.info("ℹ️ Nenhum produto cadastrado ainda. Vá para a aba 'Registro de Produtos' para cadastrar.")
            else:
                st.warning("⚠️ Perfil de produtor não encontrado. Cadastre-se na aba 'Registro de Produtos'.")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar informações: {str(e)}")
    
    # ============ TAB 2: PREVISÃO DE NECESSIDADES ============
    with tab2:
        # Obter perfil do fornecedor
        try:
            perfil_response = requests.get(
                f"{API_URL}/fornecedores/meu-perfil",
                headers=headers
            )
            
            if perfil_response.status_code != 200:
                st.warning("⚠️ Perfil de produtor não encontrado. Cadastre-se primeiro na aba 'Registro de Produtos'.")
            else:
                perfil = perfil_response.json()
                meus_produtos = [catalogo_por_id.get(p.get("produto_id"), {}).get("nome", "").lower() for p in perfil.get("produtos", [])]
                
                if not meus_produtos:
                    st.info("ℹ️ Você ainda não cadastrou produtos. Vá para a aba 'Registro de Produtos' para cadastrar.")
                else:
                    # Obter ordem de prioridade
                    try:
                        ordem_response = requests.get(
                            f"{API_URL}/fornecedores/ordem",
                            headers=headers
                        )
                        ordem_data = ordem_response.json() if ordem_response.status_code == 200 else []
                    except:
                        ordem_data = []
                    
                    # Criar mapa de prioridade e capacidade
                    prioridade_map = {}
                    capacidade_map = {}
                    for p in perfil.get("produtos", []):
                        pid = p.get("produto_id")
                        nome_prod = catalogo_por_id.get(pid, {}).get("nome", "").lower()
                        prioridade_map[nome_prod] = None
                        capacidade_map[nome_prod] = p.get("capacidade", 0)
                        
                        # Encontrar posição na ordem de prioridade
                        for ordem_item in ordem_data:
                            if ordem_item["produto"].lower() == nome_prod:
                                fornecedores_ids = ordem_item.get("fornecedores_ids", [])
                                if perfil["id"] in fornecedores_ids:
                                    prioridade_map[nome_prod] = fornecedores_ids.index(perfil["id"]) + 1
                                break
                    
                    st.subheader("🔍 Previsão de Fornecimento dos Meus Produtos")
                    # Construir lista de nomes dos meus produtos
                    meus_nomes = [catalogo_por_id.get(p.get('produto_id'), {}).get('nome', '') 
                                  for p in perfil.get('produtos', [])]
                    st.write(f"Produtos cadastrados: {', '.join(meus_nomes)}")
                    
                    # Seleção de semana do ano
                    import datetime
                    
                    # Obter semana e ano atual
                    hoje = date.today()
                    semana_atual = hoje.isocalendar()[1]
                    ano_selecionado = hoje.year
                    
                    semana_selecionada = st.number_input(
                        "Semana do Fornecimento",
                        min_value=1,
                        max_value=53,
                        value=semana_atual,
                        step=1,
                        key="preview_semana"
                    )
                    
                    # Calcular segunda e domingo da semana selecionada
                    def get_week_dates(year, week):
                        # Primeiro dia do ano
                        jan_1 = datetime.date(year, 1, 1)
                        # Encontrar a segunda-feira da semana 1
                        days_to_monday = (7 - jan_1.weekday()) % 7
                        if days_to_monday == 0 and jan_1.weekday() != 0:
                            days_to_monday = 7
                        week_1_monday = jan_1 + timedelta(days=days_to_monday)
                        
                        # Calcular segunda-feira da semana selecionada
                        target_monday = week_1_monday + timedelta(weeks=week - 1)
                        # Domingo é 6 dias depois
                        target_sunday = target_monday + timedelta(days=6)
                        
                        return target_monday, target_sunday
                    
                    data_inicio, data_fim = get_week_dates(int(ano_selecionado), int(semana_selecionada))
                    
                    st.info(f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} (Segunda) a {data_fim.strftime('%d/%m/%Y')} (Domingo)")
                    
                    if st.button("🔍 Ver Previsão", key="btn_preview"):
                        try:
                            response = requests.get(
                                f"{API_URL}/aprovisionamento/preview",
                                params={
                                    "data_inicio": str(data_inicio),
                                    "data_fim": str(data_fim)
                                },
                                headers=headers
                            )
                            
                            if response.status_code == 200:
                                dados = response.json()
                                
                                st.success(f"✅ Previsão gerada para {dados['periodo']}")
                                
                                # Obter todos os fornecedores para distribuir quantidades
                                try:
                                    fornecedores_response = requests.get(
                                        f"{API_URL}/fornecedores",
                                        headers=headers
                                    )
                                    todos_fornecedores = fornecedores_response.json() if fornecedores_response.status_code == 200 else []
                                except:
                                    todos_fornecedores = []
                                
                                # Criar mapa de fornecedor_id -> fornecedor
                                fornecedores_map = {f["id"]: f for f in todos_fornecedores}
                                
                                # Filtrar apenas produtos que o fornecedor produz e calcular quantidade a pedir
                                necessidades = dados.get("necessidades_previstas_historico", {})
                                necessidades_filtradas = []
                                
                                for produto, quantidade_total in necessidades.items():
                                    produto_lower = produto.lower()
                                    # Verificar se este produto está em meus produtos (comparando nomes do catálogo)
                                    if produto_lower in [n.lower() for n in meus_nomes]:
                                        # Encontrar qual é meu produto_id para este nome
                                        meu_pid = None
                                        for p in perfil.get('produtos', []):
                                            if catalogo_por_id.get(p.get('produto_id'), {}).get('nome', '').lower() == produto_lower:
                                                meu_pid = p.get('produto_id')
                                                break
                                        
                                        # Obter ordem de prioridade para este produto
                                        ordem_produto = None
                                        for ordem_item in ordem_data:
                                            if ordem_item["produto"].lower() == produto_lower:
                                                ordem_produto = ordem_item
                                                break
                                        
                                        if ordem_produto:
                                            fornecedores_ids = ordem_produto.get("fornecedores_ids", [])
                                            
                                            # Calcular quanto cada fornecedor deve fornecer
                                            quantidade_restante = quantidade_total
                                            quantidade_para_mim = 0
                                            
                                            for idx, forn_id in enumerate(fornecedores_ids):
                                                if quantidade_restante <= 0:
                                                    break
                                                
                                                # Obter capacidade do fornecedor para este produto
                                                fornecedor = fornecedores_map.get(forn_id)
                                                if fornecedor:
                                                    for p in fornecedor.get("produtos", []):
                                                        p_nome = catalogo_por_id.get(p.get("produto_id"), {}).get("nome", "").lower()
                                                        if p_nome == produto_lower:
                                                            capacidade_forn = p.get("capacidade", 0)
                                                            
                                                            # Se for o fornecedor atual (eu)
                                                            if forn_id == perfil["id"]:
                                                                # Calcular quanto devo fornecer
                                                                quantidade_para_mim = min(capacidade_forn, quantidade_restante)
                                                                quantidade_restante -= quantidade_para_mim
                                                            else:
                                                                # Fornecedor com prioridade maior já consome da necessidade
                                                                quantidade_consumida = min(capacidade_forn, quantidade_restante)
                                                                quantidade_restante -= quantidade_consumida
                                                            break
                                            
                                            # Só mostrar se houver quantidade para mim
                                            if quantidade_para_mim > 0:
                                                # Encontrar prioridade e capacidade
                                                prioridade = None
                                                capacidade = 0
                                                for p in perfil.get('produtos', []):
                                                    if p.get('produto_id') == meu_pid:
                                                        capacidade = p.get('capacidade', 0)
                                                        # Encontrar posição na ordem de prioridade
                                                        for ordem_item in ordem_data:
                                                            if ordem_item["produto"].lower() == produto_lower:
                                                                fornecedores_ids = ordem_item.get("fornecedores_ids", [])
                                                                if perfil["id"] in fornecedores_ids:
                                                                    prioridade = fornecedores_ids.index(perfil["id"]) + 1
                                                                break
                                                        break
                                                
                                                necessidades_filtradas.append({
                                                    "Produto": produto,
                                                    "Quantidade Total Necessária (kg)": quantidade_total,
                                                    "Quantidade a Fornecer (kg)": quantidade_para_mim,
                                                    "Prioridade": prioridade if prioridade else "N/A",
                                                    "Capacidade (kg)": capacidade
                                                })
                                
                                if necessidades_filtradas:
                                    # Ordenar por prioridade (valores menores = maior prioridade)
                                    necessidades_filtradas.sort(
                                        key=lambda x: (
                                            float('inf') if x["Prioridade"] == "N/A" else x["Prioridade"],
                                            -x["Capacidade (kg)"]  # Maior capacidade primeiro em caso de empate
                                        )
                                    )
                                    
                                    st.markdown("**📊 Necessidades dos Produtos que Você Deve Fornecer**")
                                    st.caption("Calculado com base na sua prioridade e capacidade disponível")
                                    
                                    df_filtrado = pd.DataFrame(necessidades_filtradas)
                                    # Mostrar apenas as colunas: Produto, Quantidade a Fornecer e Capacidade
                                    df_display = df_filtrado[["Produto", "Quantidade a Fornecer (kg)", "Capacidade (kg)"]]
                                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                                    
                                    # Resumo
                                    total_a_fornecer = sum(item["Quantidade a Fornecer (kg)"] for item in necessidades_filtradas)
                                    st.metric("Total a Fornecer", f"{total_a_fornecer:.2f} kg")
                                else:
                                    st.info("ℹ️ Nenhum dos seus produtos é necessário para este período ou sua capacidade já foi atendida por fornecedores de maior prioridade.")
                            
                            else:
                                st.error(f"❌ Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao conectar com API: {str(e)}")
                            
        except Exception as e:
            st.error(f"❌ Erro ao obter perfil: {str(e)}")
    
    # ============ TAB 3: REGISTRO DE PRODUTOS ============
    with tab3:
        st.subheader("📝 Registro de Produtor")
        
        # Obter dados do perfil (sempre existirá para produtores)
        try:
            perfil_response = requests.get(
                f"{API_URL}/fornecedores/meu-perfil",
                headers=headers
            )
            
            if perfil_response.status_code == 200:
                perfil = perfil_response.json()
                nome = perfil.get("nome", "N/A")
                data_inscricao_str = perfil.get("data_inscricao", "N/A")
                
                # Obter produtos já registados
                produtos_registados = perfil.get("produtos", [])
                produtos_registados_ids = {p.get("produto_id") for p in produtos_registados}
                
                # Mostrar dados não editáveis
                st.metric("Nome do Produtor", nome)
                st.metric("Data de Inscrição", data_inscricao_str)
                
                # Mostrar produtos já registados
                if produtos_registados:
                    st.info(f"ℹ️ Você já tem {len(produtos_registados)} produto(s) registado(s). Não pode registar o mesmo produto duas vezes.")
                
                # Converter string para objeto date
                try:
                    data_inscricao = date.fromisoformat(data_inscricao_str)
                except:
                    data_inscricao = date.today()
            else:
                st.error("❌ Erro ao carregar perfil do produtor.")
                nome = "Erro"
                data_inscricao = date.today()
                produtos_registados_ids = set()
        except Exception as e:
            st.error(f"❌ Erro ao conectar com API: {str(e)}")
            nome = "Erro"
            data_inscricao = date.today()
            produtos_registados_ids = set()

        st.subheader("Produtos")

        # Buscar catálogo de produtos do backend
        try:
            cat_resp = requests.get(f"{API_URL}/produtos-catalogo/")
            cat_resp.raise_for_status()
            catalogo_novo = cat_resp.json()
        except Exception as e:
            st.error(f"Erro ao carregar catálogo: {str(e)}")
            catalogo_novo = []

        # Mapa id->produto e lista (nome, id) ordenada, excluindo produtos já registados
        catalogo_por_id_novo = {p["id"]: p for p in catalogo_novo}
        nomes_e_ids_novo = [(p.get("nome", ""), p["id"]) for p in catalogo_novo if p["id"] not in produtos_registados_ids]
        nomes_e_ids_novo.sort(key=lambda x: x[0].lower())
        nomes_display_novo = [nome for nome, _ in nomes_e_ids_novo]
        
        if not nomes_display_novo:
            st.warning("⚠️ Não há mais produtos disponíveis para registo. Você já registou todos os produtos que oferece.")
        else:
            opcoes_novo = [""] + nomes_display_novo
            prod_nome = st.selectbox("Produto", options=opcoes_novo)
            
            # Obter produto_id selecionado
            produto_id = None
            if prod_nome:
                for n, pid in nomes_e_ids_novo:
                    if n == prod_nome:
                        produto_id = pid
                        break
            
            # Mostrar tipo do catálogo
            if produto_id and produto_id in catalogo_por_id_novo:
                tipo_produto = catalogo_por_id_novo[produto_id].get("tipo")
                if tipo_produto:
                    st.info(f"📦 Tipo: **{tipo_produto}**")
            
            biologico = st.checkbox("Produto Biológico", value=True)

            prod_ini = st.date_input("Início intervalo produção", value=date.today())
            prod_fim = st.date_input("Fim intervalo produção", value=date.today())
            capacidade = st.number_input("Capacidade (Kg)", min_value=0, value=0)

            if st.button("Submeter inscrição"):
                if produto_id:
                    payload = {
                        "nome": nome,
                        "data_inscricao": str(data_inscricao),
                        "produtos": [
                            {
                                "produto_id": produto_id,
                            "biologico": biologico,
                            "intervalo_producao_inicio": str(prod_ini),
                            "intervalo_producao_fim": str(prod_fim),
                            "capacidade": int(capacidade),
                        }
                    ],
                }
                try:
                    novo = create_fornecedor(API_URL, auth_token, payload)
                    st.success(f"Produtor criado com id {novo['id']} (aguarda aprovação).")
                except Exception as e:
                    st.error(f"❌ Erro ao criar produtor: {str(e)}")
            else:
                st.error("Selecione um produto válido do catálogo!")
