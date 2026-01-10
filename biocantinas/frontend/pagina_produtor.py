import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd

def create_fornecedor(API_URL, auth_token, payload):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.post(f"{API_URL}/fornecedores", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def adicionar_produto_fornecedor(API_URL, auth_token, payload):
    """Adiciona um novo produto ao fornecedor do usuário logado"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.post(f"{API_URL}/fornecedores/meu-perfil/produtos", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_produtor(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Aplicar estilo customizado para as abas e métricas
    st.markdown("""
        <style>
        /* Estilo para as abas */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 24px !important;
            font-weight: 600 !important;
        }
        /* Estilo para as tabelas */
        [data-testid="stDataFrame"] {
            font-size: 16px !important;
        }
        [data-testid="stDataFrame"] th {
            font-size: 16px !important;
            font-weight: bold !important;
        }
        [data-testid="stDataFrame"] td {
            font-size: 15px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
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
        st.space()
        try:
            perfil_response = requests.get(
                f"{API_URL}/fornecedores/meu-perfil",
                headers=headers
            )
            
            if perfil_response.status_code == 200:
                perfil = perfil_response.json()
                
                # Calcular produtos aprovados e não aprovados
                produtos = perfil.get("produtos", [])
                total_produtos = len(produtos)
                
                # Se o fornecedor está aprovado, todos os produtos estão aprovados
                if perfil.get("aprovado"):
                    produtos_aprovados = total_produtos
                    produtos_nao_aprovados = 0
                else:
                    produtos_aprovados = 0
                    produtos_nao_aprovados = total_produtos
                
                # Mostrar nome, data de inscrição, e status dos produtos
                # Linha 1: 5 colunas
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(f"<h3>👤 Nome Registado</h3><h2>{perfil.get('nome', 'N/A')}</h2>", unsafe_allow_html=True)
                with col2:
                    data_inscricao = perfil.get("data_inscricao", "N/A")
                    st.write(f"<h3>📅 Data de Inscrição</h3><h2>{data_inscricao}</h2>", unsafe_allow_html=True)
                # col3, col4, col5 ficam em branco
                
                st.space()
                
                # Linha 2: 5 colunas
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(f"<h3>📦 Total Produtos Cadastrados</h3><h2>{len(produtos)}</h2>", unsafe_allow_html=True)
                with col2:
                    st.write(f"<h3>✅ Produtos Aprovados</h3><h2>{produtos_aprovados}</h2>", unsafe_allow_html=True)
                with col3:
                    st.write(f"<h3>⏳ Produtos Pendentes</h3><h2>{produtos_nao_aprovados}</h2>", unsafe_allow_html=True)
                # col4 e col5 ficam em branco
                
                st.divider()
                
                produtos = perfil.get("produtos", [])
                
                # Obter semana atual
                from datetime import date as date_class
                semana_atual = date_class.today().isocalendar()[1]
                
                # Obter ordem de prioridade (considerando semana atual)
                try:
                    ordem_response = requests.get(
                        f"{API_URL}/fornecedores/ordem",
                        params={"semana": int(semana_atual)},
                        headers=headers
                    )
                    ordem_data = ordem_response.json() if ordem_response.status_code == 200 else []
                except:
                    ordem_data = []
                
                if produtos:               
                    # Tabela de produtos
                    st.markdown("### 🌱 Produtos Cadastrados")
                    produtos_info = []
                    for produto in produtos:
                        # Encontrar prioridade
                        prioridade = None
                        for ordem_item in ordem_data:
                            if ordem_item["produto"].lower() == produto["nome"].lower():
                                fornecedores_ids = ordem_item.get("fornecedores_ids", [])
                                if perfil["id"] in fornecedores_ids:
                                    prioridade = fornecedores_ids.index(perfil["id"]) + 1
                                break
                        
                        # Indicador visual para biológico/não-biológico
                        biologico_label = "✅ Sim" if produto.get("biologico") else "❌ Não"
                        
                        # Verificar se tem certificado
                        cert_label = "✅ Sim" if produto.get("certificado") else "❌ Não"
                        
                        # Status do produto (depende do status do fornecedor)
                        status_label = "✅ Aprovado" if perfil.get("aprovado") else "⏳ Pendente"
                        
                        # Capacidade e unidade separadas
                        unidade = produto.get("unidade", "kg")
                        
                        produtos_info.append({
                            "Produto": produto.get("nome", ""),
                            "Biologico": biologico_label,
                            "Capacidade": produto.get('capacidade', 0),
                            "Unidade": unidade,
                            "Semana Início": produto.get("semana_producao_inicio", "N/A"),
                            "Semana Fim": produto.get("semana_producao_fim", "N/A"),
                            "Certificado": cert_label,
                            "Status": status_label,
                            "Prioridade": prioridade if prioridade else "N/A"
                        })
                    
                    df_produtos = pd.DataFrame(produtos_info)
                    
                    # Exibir tabela com HTML para ter mais controle sobre o tamanho da fonte
                    html_table = df_produtos.to_html(index=False, escape=False)
                    html_table = html_table.replace('<table', '<table style="font-size: 18px; width: 100%;"')
                    html_table = html_table.replace('<th', '<th style="font-size: 18px; font-weight: bold; padding: 12px; text-align: left;"')
                    html_table = html_table.replace('<td', '<td style="font-size: 17px; padding: 10px;"')
                    st.write(html_table, unsafe_allow_html=True)
                    
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
                meus_produtos = [p["nome"].lower() for p in perfil.get("produtos", [])]
                
                if not meus_produtos:
                    st.info("ℹ️ Você ainda não cadastrou produtos. Vá para a aba 'Registro de Produtos' para cadastrar.")
                else:
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
                    
                    # Obter ordem de prioridade (considerando semana selecionada)
                    try:
                        ordem_response = requests.get(
                            f"{API_URL}/fornecedores/ordem",
                            params={"semana": int(semana_selecionada)},
                            headers=headers
                        )
                        ordem_data = ordem_response.json() if ordem_response.status_code == 200 else []
                    except:
                        ordem_data = []
                    
                    # Criar mapa de prioridade e capacidade
                    prioridade_map = {}
                    capacidade_map = {}
                    unidade_map = {}
                    for p in perfil.get("produtos", []):
                        produto_nome = p["nome"].lower()
                        prioridade_map[produto_nome] = None
                        capacidade_map[produto_nome] = p.get("capacidade", 0)
                        unidade_map[produto_nome] = p.get("unidade", "kg")
                        
                        # Encontrar posição na ordem de prioridade
                        for ordem_item in ordem_data:
                            if ordem_item["produto"].lower() == produto_nome:
                                fornecedores_ids = ordem_item.get("fornecedores_ids", [])
                                if perfil["id"] in fornecedores_ids:
                                    prioridade_map[produto_nome] = fornecedores_ids.index(perfil["id"]) + 1
                                break
                    
                    st.subheader("🔍 Previsão de Fornecimento dos Meus Produtos")
                    st.write(f"Produtos cadastrados: {', '.join([p['nome'] for p in perfil.get('produtos', [])])}")
                    
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
                                necessidades = dados.get("necessidades_ajustadas", dados.get("necessidades_previstas_historico", {}))
                                necessidades_filtradas = []
                                
                                for produto, quantidade_total in necessidades.items():
                                    produto_lower = produto.lower()
                                    if produto_lower in meus_produtos:
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
                                                        if p["nome"].lower() == produto_lower:
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
                                                prioridade = prioridade_map.get(produto_lower)
                                                capacidade = capacidade_map.get(produto_lower, 0)
                                                necessidades_filtradas.append({
                                                    "Produto": produto,
                                                    "Quantidade Total Necessária (kg)": quantidade_total,
                                                    "Quantidade a Fornecer (kg)": quantidade_para_mim,
                                                    "Prioridade": prioridade if prioridade else "N/A",
                                                    "Capacidade": capacidade,
                                                    "Unidade": unidade_map.get(produto_lower, "kg")
                                                })
                                
                                if necessidades_filtradas:
                                    # Ordenar por prioridade (valores menores = maior prioridade)
                                    necessidades_filtradas.sort(
                                        key=lambda x: (
                                            float('inf') if x["Prioridade"] == "N/A" else x["Prioridade"],
                                            -x["Capacidade"]  # Maior capacidade primeiro em caso de empate
                                        )
                                    )
                                    
                                    st.markdown("**📊 Necessidades dos Produtos que Você Deve Fornecer**")
                                    st.caption("Calculado com base na sua prioridade e capacidade disponível")
                                    
                                    df_filtrado = pd.DataFrame(necessidades_filtradas)
                                    # Mostrar apenas as colunas: Produto, Quantidade a Fornecer e Capacidade
                                    df_display = df_filtrado[["Produto", "Quantidade a Fornecer (kg)", "Capacidade", "Unidade"]]
                                    st.dataframe(df_display, width='stretch', hide_index=True)
                                    
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
                
                # Mostrar dados não editáveis
                st.metric("Nome do Produtor", nome)
                st.metric("Data de Inscrição", data_inscricao_str)
                
                # Converter string para objeto date
                try:
                    data_inscricao = date.fromisoformat(data_inscricao_str)
                except:
                    data_inscricao = date.today()
            else:
                st.error("❌ Erro ao carregar perfil do produtor.")
                nome = "Erro"
                data_inscricao = date.today()
        except Exception as e:
            st.error(f"❌ Erro ao conectar com API: {str(e)}")
            nome = "Erro"
            data_inscricao = date.today()

        st.subheader("Produtos")

        # Lista fixa de produtos com seus tipos (mesma do formulário de registro)
        PRODUTOS_DISPONIVEIS = {
            "Frutas": {
                "Maçã": "Fruta",
                "Pera": "Fruta",
                "Laranja": "Fruta",
                "Banana": "Fruta",
                "Morango": "Fruta",
                "Uva": "Fruta",
                "Pêssego": "Fruta",
                "Ameixa": "Fruta",
                "Melancia": "Fruta",
                "Melão": "Fruta"
            },
            "Hortícolas": {
                "Tomate": "Hortícola",
                "Alface": "Hortícola",
                "Cenoura": "Hortícola",
                "Batata": "Hortícola",
                "Cebola": "Hortícola",
                "Couve": "Hortícola",
                "Brócolos": "Hortícola",
                "Pimento": "Hortícola",
                "Beringela": "Hortícola",
                "Abóbora": "Hortícola",
                "Feijão-verde": "Hortícola",
                "Espinafre": "Hortícola"
            },
            "Proteínas": {
                "Frango": "Proteína",
                "Carne de Vaca": "Proteína",
                "Carne de Porco": "Proteína",
                "Peixe": "Proteína",
                "Ovos": "Proteína",
                "Tofu": "Proteína",
                "Grão-de-bico": "Proteína",
                "Lentilhas": "Proteína"
            },
            "Cereais": {
                "Arroz": "Cereais",
                "Massa": "Cereais",
                "Pão": "Cereais",
                "Aveia": "Cereais",
                "Quinoa": "Cereais",
                "Milho": "Cereais"
            },
            "Laticínios": {
                "Leite": "Laticínios",
                "Queijo": "Laticínios",
                "Iogurte": "Laticínios",
                "Manteiga": "Laticínios",
                "Nata": "Laticínios"
            },
            "Outros": {
                "Azeite": "Outro",
                "Mel": "Outro",
                "Ervas Aromáticas": "Outro",
                "Especiarias": "Outro"
            }
        }

        # Criar lista plana de produtos
        todos_produtos = []
        for categoria, produtos in PRODUTOS_DISPONIVEIS.items():
            todos_produtos.extend(produtos.keys())

        prod_nome = st.selectbox("Produto", options=[""] + todos_produtos)
        
        # Determinar automaticamente o tipo baseado no produto selecionado
        tipo_produto = None
        if prod_nome:
            for categoria, produtos in PRODUTOS_DISPONIVEIS.items():
                if prod_nome in produtos:
                    tipo_produto = produtos[prod_nome]
                    break
        
        if tipo_produto:
            st.info(f"📦 Tipo: **{tipo_produto}**")
        
        biologico = st.checkbox("Produto Biológico", value=True)

        col_semanas = st.columns(2)
        with col_semanas[0]:
            semana_inicio = st.number_input("Semana de Início (1-52)", min_value=1, max_value=52, value=1)
        with col_semanas[1]:
            semana_fim = st.number_input("Semana de Fim (1-52)", min_value=1, max_value=52, value=52)
        
        col_cap = st.columns(2)
        with col_cap[0]:
            capacidade = st.number_input("Capacidade", min_value=0, value=0)
        with col_cap[1]:
            unidade = st.selectbox("Unidade", options=["kg", "L", "unidades", "caixas", "outro"], index=0)
        
        st.divider()
        st.subheader("📜 Certificação")
        
        if not biologico:
            st.warning("⚠️ Certificação é aplicável apenas para produtos biológicos. Marque 'Produto Biológico' acima.")
        
        certificado_texto = st.text_area(
            "Informações de Certificação",
            placeholder="Ex: Certificado biológico nº XYZ123, válido até 2025-12-31",
            height=100,
            disabled=not biologico
        )
        
        arquivo_certificado = st.file_uploader(
            "Anexar documento de certificação",
            type=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
            disabled=not biologico
        )
        
        certificado_info = None
        if biologico and (certificado_texto or arquivo_certificado):
            certificado_info = certificado_texto
            if arquivo_certificado:
                certificado_info = f"{certificado_texto}\n[Arquivo: {arquivo_certificado.name}]" if certificado_texto else f"[Arquivo: {arquivo_certificado.name}]"

        if st.button("Submeter inscrição"):
            if prod_nome and tipo_produto:
                payload = {
                    "nome": prod_nome,
                    "biologico": biologico,
                    "semana_producao_inicio": int(semana_inicio),
                    "semana_producao_fim": int(semana_fim),
                    "capacidade": int(capacidade),
                    "unidade": unidade,
                    "certificado": certificado_info,
                }
                try:
                    resultado = adicionar_produto_fornecedor(API_URL, auth_token, payload)
                    st.success(f"✅ Produto '{prod_nome}' adicionado com sucesso ao seu perfil!")
                    # Rerun para atualizar a tabela de produtos
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao adicionar produto: {str(e)}")
            else:
                st.error("Selecione um produto válido!")
