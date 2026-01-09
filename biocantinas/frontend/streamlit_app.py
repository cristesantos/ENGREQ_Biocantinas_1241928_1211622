import streamlit as st
import requests
from datetime import date
import threading
import uvicorn
import sys
import os
from pathlib import Path
import base64

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

st.set_page_config(page_title="BioCantinas - Fornecedores", layout="wide")


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
    # Carregar e converter imagem de fundo para base64
    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            return None
    
    # Tentar carregar a imagem
    img_path = Path(__file__).parent / "fundo_main.jpg"
    bg_image = get_base64_image(img_path)
    
    if bg_image:
        # CSS para adicionar imagem de fundo com 50% de opacidade
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{bg_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(255, 255, 255, 0.5);
                z-index: -1;
                pointer-events: none;
            }}
            </style>
        """, unsafe_allow_html=True)
    
    # Centralizar e reduzir o tamanho da área de login
    col_left, col_center, col_right = st.columns([2, 1, 2])
    
    with col_center:
        # Container com fundo branco
        st.markdown("""
            <style>
            div[data-testid="column"]:nth-child(2) {{
                background-color: white !important;
                padding: 1.5rem !important;
                border-radius: 15px !important;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
                max-width: 400px !important;
                margin: 0 auto !important;
            }}
            div[data-testid="column"]:nth-child(2) > div {{
                background-color: white !important;
            }}
            /* Reduzir tamanho dos inputs */
            div[data-testid="column"]:nth-child(2) input {{
                font-size: 0.9rem !important;
                padding: 0.4rem !important;
            }}
            /* Reduzir tamanho dos botões */
            div[data-testid="column"]:nth-child(2) button {{
                font-size: 0.9rem !important;
                padding: 0.4rem 0.8rem !important;
            }}
            /* Reduzir tamanho dos selectbox */
            div[data-testid="column"]:nth-child(2) .stSelectbox {{
                font-size: 0.9rem !important;
            }}
            /* Reduzir espaçamento */
            div[data-testid="column"]:nth-child(2) .stTextInput {{
                margin-bottom: 0.5rem !important;
            }}
            </style>
        """, unsafe_allow_html=True)
        
        # Logo centralizada
        logo_login_path = Path(__file__).parent / "Biocantinas.png"
        if logo_login_path.exists():
            col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
            with col_logo2:
                st.image(str(logo_login_path), width='stretch')
        
        st.markdown("<h2 style='text-align: center;'>Bem vindo!</h2>", unsafe_allow_html=True)
        
        # Botões para alternar entre Login e Registro
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔑 Login", width='stretch', type="primary" if not st.session_state.show_register else "secondary"):
                st.session_state.show_register = False
                st.rerun()
        with col2:
            if st.button("📝 Registrar", width='stretch', type="primary" if st.session_state.show_register else "secondary"):
                st.session_state.show_register = True
                st.rerun()
        
        st.divider()
        
        # Mostrar apenas o formulário correspondente
        if st.session_state.show_register:
            st.subheader("Criar nova conta")
            reg_username = st.text_input("Usuário", key="reg_username")
            reg_password = st.text_input("Senha", type="password", key="reg_password")
            reg_role = st.selectbox("Papel", ["GESTOR", "PRODUTOR", "GESTOR_CANTINA", "DIETISTA"], key="reg_role")
            
            # Mostrar formulário adicional para PRODUTOR assim que for selecionado
            if reg_role == "PRODUTOR":
                st.divider()
                st.subheader("📝 Dados do Produtor")
                st.info("Complete os dados do seu perfil de produtor")
                
                produtor_nome = st.text_input("Nome do Produtor/Empresa", key="produtor_nome")
                st.caption(f"📅 Data de Inscrição: {date.today().strftime('%Y-%m-%d')}")
                
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
                        
                        # Seção de certificação (apenas para produtos biológicos)
                        st.divider()
                        st.subheader("📜 Certificação")
                        
                        if not biologico:
                            st.caption("⚠️ Certificação é aplicável apenas para produtos biológicos.")
                        
                        certificado_texto = st.text_area(
                            "Informações de Certificação",
                            placeholder="Ex: Certificado biológico nº XYZ123, válido até 2025-12-31",
                            height=80,
                            disabled=not biologico,
                            key=f"prod_cert_texto_{i}"
                        )
                        
                        arquivo_certificado = st.file_uploader(
                            "Anexar documento de certificação",
                            type=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
                            disabled=not biologico,
                            key=f"prod_cert_arquivo_{i}"
                        )
                        
                        certificado_info = None
                        if biologico and (certificado_texto or arquivo_certificado):
                            certificado_info = certificado_texto
                            if arquivo_certificado:
                                certificado_info = f"{certificado_texto}\n[Arquivo: {arquivo_certificado.name}]" if certificado_texto else f"[Arquivo: {arquivo_certificado.name}]"
                        
                        if nome_produto and tipo_produto:
                            produtos_list.append({
                                "nome": nome_produto,
                                "tipo": tipo_produto,
                                "biologico": biologico,
                                "capacidade": capacidade,
                                "intervalo_producao_inicio": str(data_inicio),
                                "intervalo_producao_fim": str(data_fim),
                                "certificado": certificado_info
                            })
                
                # Botão de criar conta para PRODUTOR (com validação completa)
                if st.button("Criar conta", width='stretch', type="primary"):
                    if reg_username and reg_password and produtor_nome and len(produtos_list) > 0:
                        try:
                            # 1. Criar usuário
                            user_response = requests.post(
                                f"{API_URL}/auth/signup",
                                json={"username": reg_username, "password": reg_password, "role": "PRODUTOR"}
                            )
                            
                            if user_response.status_code in [200, 201]:
                                # 2. Fazer login para obter token
                                login_response = requests.post(
                                    f"{API_URL}/auth/login",
                                    json={"username": reg_username, "password": reg_password}
                                )
                                
                                if login_response.status_code == 200:
                                    token = login_response.json()["access_token"]
                                    headers = {"Authorization": f"Bearer {token}"}
                                    
                                    # 3. Criar fornecedor (usando nome customizado)
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
                                        st.success("✅ Cadastro de produtor realizado com sucesso!")
                                        st.info("Aguarde a aprovação do gestor. Faça login para acessar sua área.")
                                        st.session_state.show_register = False
                                        st.rerun()
                                    else:
                                        st.error(f"Erro ao cadastrar fornecedor: {fornecedor_response.json().get('detail', 'Erro desconhecido')}")
                                else:
                                    st.error("Erro ao fazer login automático")
                            else:
                                st.error(f"Erro no registro: {user_response.json().get('detail', 'Erro desconhecido')}")
                        except Exception as e:
                            st.error(f"Erro ao finalizar cadastro: {str(e)}")
                    else:
                        st.error("Preencha todos os campos: usuário, senha, nome do produtor e pelo menos um produto!")
            
            else:
                # Para outros papéis (não PRODUTOR), botão simples
                if st.button("Criar conta", width='stretch', type="primary"):
                    if reg_username and reg_password:
                        register(reg_username, reg_password, reg_role)
                    else:
                        st.error("Preencha todos os campos!")
        else:
            # Formulário de Login
            st.subheader("Entrar na conta")
            username = st.text_input("Usuário", key="username")
            password = st.text_input("Senha", type="password", key="password")
            if st.button("Entrar", width='stretch', type="primary"):
                if username and password:
                    login(username, password)
                else:
                    st.error("Preencha todos os campos!")
    st.stop()


# ============================================================
#  6. Sidebar e navegação (usuário autenticado)
# ============================================================

# Adicionar logo no sidebar
logo_path = Path(__file__).parent / "Biocantinas.png"
if logo_path.exists():
    st.sidebar.image(str(logo_path), width='stretch')

st.sidebar.divider()

# Criar container para botão logout com fundo vermelho
col = st.sidebar.container()
if col.button("🚪 Logout", width='stretch', key="logout_btn", type="primary"):
    logout()
    st.rerun()

# CSS específico para o botão de logout
st.markdown("""
    <style>
    /* Estilizar apenas o botão de logout */
    button[kind="primary"] {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
    }
    button[kind="primary"]:hover {
        background-color: #c82333 !important;
        border-color: #bd2130 !important;
    }
    button[kind="primary"]:active {
        background-color: #bd2130 !important;
        border-color: #b21f2d !important;
    }
    </style>
""", unsafe_allow_html=True)

# Filtrar páginas por papel do usuário
user_role = str((st.session_state.user_info or {}).get("role", "OUTRO")).upper()
paginas_disponiveis = []

if user_role == "GESTOR":
    paginas_disponiveis.append("Gestor")
if user_role in ["PRODUTOR", "FORNECEDOR"]:
    paginas_disponiveis.append("Produtor")
if user_role == "GESTOR_CANTINA":
    paginas_disponiveis.append("Gestor Cantina")
if user_role == "DIETISTA":
    paginas_disponiveis.append("Dietista")

# Se não houver páginas específicas, mostrar página inicial
if not paginas_disponiveis:
    paginas_disponiveis.append("Página inicial")

pagina = st.sidebar.radio("Perfil", paginas_disponiveis) if len(paginas_disponiveis) > 1 else paginas_disponiveis[0]


# ============================================================
#  7. Página inicial
# ============================================================

if pagina == "Página inicial":
    st.header("Bem-vindo ao BioCantinas!")


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

elif pagina == "Dietista" and str(st.session_state.user_info.get("role", "")).upper() == "DIETISTA":
    from pagina_dietista import pagina_dietista
    pagina_dietista(API_URL, st.session_state.auth_token)

else:
    st.error("Acesso negado: você não tem permissão para acessar esta página.")
