import streamlit as st
import requests
from datetime import date
import threading
import uvicorn
import sys
import os
from pathlib import Path

# ============================================================
#  1. Ajustar sys.path para garantir import do backend
# ============================================================

ROOT = Path(__file__).resolve().parents[1]   # pasta que contém "backend"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ============================================================
#  2. Resolver API_URL (prioridade: secrets → env → local)
# ============================================================

def _resolve_api_url():
    url = None
    try:
        url = st.secrets.get("API_URL") if hasattr(st, "secrets") else None
    except Exception:
        url = None

    if not url:
        url = os.getenv("API_URL")

    if not url:
        url = "http://127.0.0.1:8000"

    return url

API_URL = _resolve_api_url()

st.set_page_config(page_title="BioCantinas - Fornecedores")
st.info(f"API_URL em uso: {API_URL}")


# ============================================================
#  2.5 Inicialização do estado de sessão (autenticação)
# ============================================================

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False


# ============================================================
#  3. Importação robusta da API FastAPI local
# ============================================================

def _import_fastapi():
    """
    Tenta importar a API independentemente da estrutura de pastas.
    Funciona em desenvolvimento local.
    """
    try:
        from backend.app.main import app as api
        return api
    except Exception:
        return None

fastapi_app = _import_fastapi()


# ============================================================
#  4. Função que inicia a API FastAPI embutida
# ============================================================

def _start_api():
    print("=== Iniciando FastAPI embutida ===")
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")


def _is_running_on_cloud():
    """STREAMLIT_RUNTIME só existe no Streamlit Cloud."""
    return "STREAMLIT_RUNTIME" in os.environ


# ============================================================
#  5. Iniciar API somente localmente
# ============================================================

if (
    fastapi_app                              # backend carregado corretamente
    and not _is_running_on_cloud()           # não rodar no Streamlit Cloud
    and "api_thread_started" not in st.session_state
):
    st.session_state.api_thread = threading.Thread(
        target=_start_api,
        daemon=True
    )
    st.session_state.api_thread.start()
    st.session_state.api_thread_started = True
    st.info("FastAPI iniciada localmente na porta 8000")


# ============================================================
#  5.5 Funções de autenticação
# ============================================================

def login(username: str, password: str):
    """Faz login e armazena o token JWT."""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data["access_token"]
            # Preenche info do usuário a partir da resposta do login
            role = str(data.get("role", "OUTRO")).upper()
            st.session_state.user_info = {
                "username": data.get("username", username),
                "role": role
            }
            st.success("Login realizado com sucesso!")
            st.rerun()  # Recarrega para exibir a sidebar
        else:
            st.error(f"Erro no login: {response.json().get('detail', 'Usuário ou senha inválidos')}")
            return False
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return False


def register(username: str, password: str, role: str, keep_form_open: bool = False):
    """Registra um novo usuário."""
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            json={"username": username, "password": password,  "role": role}
        )
        if response.status_code in [200, 201]:
            if not keep_form_open:
                st.success("Usuário registrado com sucesso! Faça login agora.")
                st.session_state.show_register = False
            else:
                st.success("Usuário criado! Complete agora os dados do produtor.")
            return True
        else:
            st.error(f"Erro no registro: {response.json().get('detail', 'Erro desconhecido')}")
            return False
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return False


def logout():
    """Faz logout."""
    st.session_state.auth_token = None
    st.session_state.user_info = None
    st.success("Logout realizado!")


# ============================================================
#  5.6 Página de login/registro (se não autenticado)
# ============================================================

if not st.session_state.auth_token:
    st.header("BioCantinas - Autenticação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login", use_container_width=True):
            st.session_state.show_register = False
    with col2:
        if st.button("Registrar", use_container_width=True):
            st.session_state.show_register = True
    
    if st.session_state.show_register:
        st.subheader("Criar nova conta")
        reg_username = st.text_input("Usuário (registro)", key="reg_username")
        reg_password = st.text_input("Senha (registro)", type="password", key="reg_password")
        reg_role = st.selectbox("Papel", ["GESTOR", "PRODUTOR", "GESTOR_CANTINA", "DIETISTA"], key="reg_role")
        
        # Inicializar estado para formulário de produtor
        if "show_produtor_form" not in st.session_state:
            st.session_state.show_produtor_form = False
        if "produtor_registered" not in st.session_state:
            st.session_state.produtor_registered = False
        
        if st.button("Criar conta"):
            if reg_username and reg_password:
                # Se for PRODUTOR, mostrar formulário adicional
                if reg_role == "PRODUTOR":
                    if register(reg_username, reg_password, reg_role, keep_form_open=True):
                        st.session_state.show_produtor_form = True
                        st.session_state.temp_username = reg_username
                        st.session_state.temp_password = reg_password
                        st.rerun()
                else:
                    # Para outros papéis, registrar normalmente
                    register(reg_username, reg_password, reg_role)
            else:
                st.error("Preencha todos os campos!")
        
        # Formulário adicional para PRODUTOR
        if st.session_state.show_produtor_form and not st.session_state.produtor_registered:
            st.divider()
            st.subheader("📝 Dados do Produtor")
            st.info("Complete os dados do seu perfil de produtor")
            
            produtor_nome = st.text_input("Nome do Produtor/Empresa", key="produtor_nome")
            
            # Lista fixa de produtos com seus tipos
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
            
            st.markdown("### 🌱 Produtos")
            num_produtos = st.number_input("Quantos produtos deseja cadastrar?", min_value=1, max_value=10, value=1, key="num_produtos")
            
            produtos_list = []
            for i in range(int(num_produtos)):
                with st.expander(f"Produto {i+1}", expanded=(i==0)):
                    col1, col2 = st.columns(2)
                    with col1:
                        nome_produto = st.selectbox(
                            "Selecione o Produto", 
                            [""] + todos_produtos,
                            key=f"prod_nome_{i}"
                        )
                        
                        # Determinar automaticamente o tipo baseado no produto selecionado
                        tipo_produto = None
                        if nome_produto:
                            for categoria, produtos in PRODUTOS_DISPONIVEIS.items():
                                if nome_produto in produtos:
                                    tipo_produto = produtos[nome_produto]
                                    break
                        
                        if tipo_produto:
                            st.info(f"📦 Tipo: **{tipo_produto}**")
                        
                        biologico = st.checkbox("Produto Biológico", value=True, key=f"prod_bio_{i}")
                    with col2:
                        capacidade = st.number_input("Capacidade (kg)", min_value=1, value=100, key=f"prod_cap_{i}")
                        data_inicio = st.date_input("Início da Produção", key=f"prod_inicio_{i}")
                        data_fim = st.date_input("Fim da Produção", key=f"prod_fim_{i}")
                    
                    if nome_produto and tipo_produto:
                        produtos_list.append({
                            "nome": nome_produto,
                            "tipo": tipo_produto,
                            "biologico": biologico,
                            "capacidade": capacidade,
                            "intervalo_producao_inicio": str(data_inicio),
                            "intervalo_producao_fim": str(data_fim)
                        })
            
            if st.button("Finalizar Cadastro de Produtor"):
                if produtor_nome and len(produtos_list) > 0:
                    try:
                        # Fazer login automático para obter token
                        login_response = requests.post(
                            f"{API_URL}/auth/login",
                            json={
                                "username": st.session_state.temp_username,
                                "password": st.session_state.temp_password
                            }
                        )
                        
                        if login_response.status_code == 200:
                            token = login_response.json()["access_token"]
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            # Criar fornecedor
                            fornecedor_payload = {
                                "nome": produtor_nome,
                                "data_inscricao": str(date.today()),
                                "produtos": produtos_list
                            }
                            
                            fornecedor_response = requests.post(
                                f"{API_URL}/fornecedores",
                                json=fornecedor_payload,
                                headers=headers
                            )
                            
                            if fornecedor_response.status_code in [200, 201]:
                                st.success("✅ Cadastro de produtor finalizado com sucesso!")
                                st.info("Aguarde a aprovação do gestor para começar a fornecer produtos.")
                                st.session_state.produtor_registered = True
                                st.session_state.show_produtor_form = False
                                st.session_state.show_register = False
                                # Limpar dados temporários
                                if "temp_username" in st.session_state:
                                    del st.session_state.temp_username
                                if "temp_password" in st.session_state:
                                    del st.session_state.temp_password
                                st.rerun()
                            else:
                                st.error(f"Erro ao cadastrar fornecedor: {fornecedor_response.json().get('detail', 'Erro desconhecido')}")
                        else:
                            st.error("Erro ao fazer login automático")
                    except Exception as e:
                        st.error(f"Erro ao finalizar cadastro: {str(e)}")
                else:
                    st.error("Preencha o nome do produtor e cadastre pelo menos um produto!")
    else:
        st.subheader("Fazer login")
        username = st.text_input("Usuário", key="username")
        password = st.text_input("Senha", type="password", key="password")
        if st.button("Entrar"):
            if username and password:
                login(username, password)
            else:
                st.error("Preencha todos os campos!")
    st.stop()


# ============================================================
#  6. Sidebar e navegação (usuário autenticado)
# ============================================================

st.sidebar.title("BioCantinas")
if st.session_state.user_info:
    st.sidebar.write(f"👤 Logado como: **{st.session_state.user_info['username']}** ({st.session_state.user_info['role']})")
else:
    st.sidebar.write("👤 Não autenticado")

if st.sidebar.button("Logout"):
    logout()
    st.rerun()

# Filtrar páginas por papel do usuário
user_role = str((st.session_state.user_info or {}).get("role", "OUTRO")).upper()
paginas_disponiveis = ["Página inicial"]

if user_role == "GESTOR":
    paginas_disponiveis.append("Gestor")
if user_role in ["PRODUTOR", "FORNECEDOR"]:
    paginas_disponiveis.append("Produtor")
if user_role == "GESTOR_CANTINA":
    paginas_disponiveis.append("Gestor Cantina")
    paginas_disponiveis.append("Aprovisionamento")
if user_role == "DIETISTA":
    paginas_disponiveis.append("Dietista")

pagina = st.sidebar.radio("Perfil", paginas_disponiveis)


# ============================================================
#  7. Página inicial
# ============================================================

if pagina == "Página inicial":
    st.header("Bem-vindo ao BioCantinas!")
    if st.session_state.user_info:
        st.write(f"Você está logado como **{st.session_state.user_info['username']}** com o papel **{st.session_state.user_info['role']}**")
    else:
        st.write("Você ainda não está autenticado.")


# ============================================================
#  8. Páginas importadas
# ============================================================

elif pagina == "Gestor" and str(st.session_state.user_info.get("role", "")).upper() == "GESTOR":
    from pagina_gestor import pagina_gestor
    pagina_gestor(API_URL, st.session_state.auth_token)

elif pagina == "Produtor" and str(st.session_state.user_info.get("role", "")).upper() in ["PRODUTOR", "FORNECEDOR"]:
    from pagina_produtor import pagina_produtor
    pagina_produtor(API_URL, st.session_state.auth_token)

elif pagina == "Gestor Cantina" and str(st.session_state.user_info.get("role", "")).upper() == "GESTOR_CANTINA":
    from pagina_gestor_cantina import pagina_gestor_cantina
    pagina_gestor_cantina(API_URL, st.session_state.auth_token)

elif pagina == "Aprovisionamento" and str(st.session_state.user_info.get("role", "")).upper() == "GESTOR_CANTINA":
    from pagina_aprovisionamento import mostrar_aprovisionamento
    mostrar_aprovisionamento()

elif pagina == "Dietista" and str(st.session_state.user_info.get("role", "")).upper() == "DIETISTA":
    from pagina_dietista import pagina_dietista
    pagina_dietista(API_URL, st.session_state.auth_token)

else:
    st.error("Acesso negado: você não tem permissão para acessar esta página.")
