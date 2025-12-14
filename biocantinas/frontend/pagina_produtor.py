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
    st.header("Área do Produtor")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs([
        "📋 Minhas Informações",
        "🔍 Previsão de Necessidades",
        "📝 Registro de Produtos"
    ])
    
    # ============ TAB 1: MINHAS INFORMAÇÕES ============
    with tab1:
        st.subheader("📋 Informações do Produtor")
        
        try:
            perfil_response = requests.get(
                f"{API_URL}/fornecedores/meu-perfil",
                headers=headers
            )
            
            if perfil_response.status_code == 200:
                perfil = perfil_response.json()
                
                # Informações básicas
                st.markdown("### 🏢 Dados do Fornecedor")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Nome", perfil.get("nome", "N/A"))
                    st.metric("Status", "✅ Aprovado" if perfil.get("aprovado") else "⏳ Aguardando Aprovação")
                with col2:
                    data_inscricao = perfil.get("data_inscricao", "N/A")
                    st.metric("Data de Inscrição", data_inscricao)
                    st.metric("ID do Fornecedor", perfil.get("id", "N/A"))
                
                st.divider()
                
                # Produtos cadastrados
                st.markdown("### 🌱 Produtos Cadastrados")
                produtos = perfil.get("produtos", [])
                
                if produtos:
                    # Obter ordem de prioridade
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
                        for ordem_item in ordem_data:
                            if ordem_item["produto"].lower() == produto["nome"].lower():
                                fornecedores_ids = ordem_item.get("fornecedores_ids", [])
                                if perfil["id"] in fornecedores_ids:
                                    prioridade = fornecedores_ids.index(perfil["id"]) + 1
                                break
                        
                        produtos_info.append({
                            "Produto": produto.get("nome", ""),
                            "Tipo": produto.get("tipo", "N/A"),
                            "Capacidade (kg)": produto.get("capacidade", 0),
                            "Início Produção": produto.get("intervalo_producao_inicio", "N/A"),
                            "Fim Produção": produto.get("intervalo_producao_fim", "N/A"),
                            "Prioridade": prioridade if prioridade else "N/A"
                        })
                    
                    df_produtos = pd.DataFrame(produtos_info)
                    st.dataframe(df_produtos, use_container_width=True, hide_index=True)
                    
                    # Resumo estatístico
                    st.markdown("### 📊 Resumo")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Produtos", len(produtos))
                    with col2:
                        capacidade_total = sum(p.get("capacidade", 0) for p in produtos)
                        st.metric("Capacidade Total", f"{capacidade_total} kg")
                    with col3:
                        produtos_prioridade_1 = sum(1 for p in produtos_info if p["Prioridade"] == 1)
                        st.metric("Produtos com Prioridade 1", produtos_prioridade_1)
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
                        produto_nome = p["nome"].lower()
                        prioridade_map[produto_nome] = None
                        capacidade_map[produto_nome] = p.get("capacidade", 0)
                        
                        # Encontrar posição na ordem de prioridade
                        for ordem_item in ordem_data:
                            if ordem_item["produto"].lower() == produto_nome:
                                fornecedores_ids = ordem_item.get("fornecedores_ids", [])
                                if perfil["id"] in fornecedores_ids:
                                    prioridade_map[produto_nome] = fornecedores_ids.index(perfil["id"]) + 1
                                break
                    
                    st.subheader("🔍 Previsão de Necessidades dos Meus Produtos")
                    st.write(f"Produtos cadastrados: {', '.join([p['nome'] for p in perfil.get('produtos', [])])}")
                    
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
                                
                                # Filtrar apenas produtos que o fornecedor produz
                                necessidades = dados.get("necessidades_previstas_historico", {})
                                necessidades_filtradas = []
                                
                                for produto, quantidade in necessidades.items():
                                    produto_lower = produto.lower()
                                    if produto_lower in meus_produtos:
                                        prioridade = prioridade_map.get(produto_lower)
                                        capacidade = capacidade_map.get(produto_lower, 0)
                                        necessidades_filtradas.append({
                                            "Produto": produto,
                                            "Quantidade Necessária (kg)": quantidade,
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
                                    
                                    st.markdown("**📊 Necessidades dos Produtos que Você Produz**")
                                    st.caption("Ordenado por prioridade de fornecimento e capacidade")
                                    
                                    df_filtrado = pd.DataFrame(necessidades_filtradas)
                                    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                                else:
                                    st.info("ℹ️ Nenhum dos seus produtos é necessário para este período.")
                            
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

        # Lista única de produtos (sem categorias)
        produtos = [
            "kiwi", "mirtilo", "frutos vermelhos", "cereja", "maçã", "pera", "castanha",
            "couves", "alface", "rúcula", "espinafre", "tomate", "pimento", "beringela",
            "cenoura", "nabo", "beterraba", "abóbora", "curgete", "bovino", "suíno",
            "ovino", "caprino", "ovos de galinhas ao ar livre", "mel", "cogumelo shiitake",
            "frango", "carne de vaca", "peru", "vitela"
        ]

        # Ordenar alfabeticamente (independente de maiúsculas/minúsculas)
        produtos = sorted(produtos, key=lambda s: s.lower())

        prod_nome = st.selectbox("Produto", options=produtos)
        # Opcional: permitir especificar outro texto caso necessário
        if st.checkbox("Outro (especificar manualmente)"):
            prod_nome = st.text_input("Especifique o produto", value=prod_nome)

        prod_ini = st.date_input("Início intervalo produção", value=date.today())
        prod_fim = st.date_input("Fim intervalo produção", value=date.today())
        capacidade = st.number_input("Capacidade (Kg)", min_value=0, value=0)

        if st.button("Submeter inscrição"):
            payload = {
                "nome": nome,
                "data_inscricao": str(data_inscricao),
                "produtos": [
                    {
                        "nome": prod_nome,
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
