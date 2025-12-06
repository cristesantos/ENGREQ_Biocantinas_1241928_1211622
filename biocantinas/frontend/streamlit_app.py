import streamlit as st
import requests
from datetime import date
import threading
import uvicorn
import sys
import os
from pathlib import Path


def _resolve_api_url():
    """Resolve a API URL com precedência: st.secrets -> ENV -> localhost."""
    url = None
    # 1) st.secrets (Streamlit Cloud or local .streamlit/secrets.toml)
    try:
        url = st.secrets.get("API_URL") if hasattr(st, "secrets") else None
    except Exception:
        url = None

    # 2) variável de ambiente
    if not url:
        url = os.getenv("API_URL")

    # 3) fallback
    if not url:
        url = "http://127.0.0.1:8000"

    return url


API_URL = _resolve_api_url()

st.set_page_config(page_title="BioCantinas - Fornecedores")
st.info(f"API_URL em uso: {API_URL}")

# Tentar importar o app FastAPI localmente; se falhar, desativar servidor embebido
fastapi_app = None
try:
    from biocantinas.backend.app.main import app as fastapi_app
except ImportError:
    # Em ambiente de deploy (ex: Streamlit Cloud), a estrutura é diferente
    # Tentar adicionar o path pai ao sys.path e reimportar
    try:
        backend_path = Path(__file__).parent.parent / "backend"
        if backend_path.exists():
            sys.path.insert(0, str(backend_path.parent))
            from biocantinas.backend.app.main import app as fastapi_app
    except ImportError:
        st.warning("⚠️ Servidor FastAPI embebido não disponível. Certifique-se que a API está a correr em http://127.0.0.1:8000")
        fastapi_app = None

# Start FastAPI server once per Streamlit session (apenas se disponível localmente)
def _start_api():
    if fastapi_app:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")

if fastapi_app and "api_thread_started" not in st.session_state:
    st.session_state.api_thread = threading.Thread(target=_start_api, daemon=True)
    st.session_state.api_thread.start()
    st.session_state.api_thread_started = True
    st.info("FastAPI iniciado em background na porta 8000")

st.sidebar.title("BioCantinas")

# Auth state
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

st.header("Autenticação")
colA, colB = st.columns([3,1])
with colB:
    if st.button("Alternar para Sign up" if st.session_state.auth_mode == "login" else "Alternar para Login"):
        st.session_state.auth_mode = "signup" if st.session_state.auth_mode == "login" else "login"
        st.rerun()

with colA:
    user_in = st.text_input("Utilizador", value=st.session_state.username or "")
    pass_in = st.text_input("Password", type="password")
    if st.session_state.auth_mode == "login":
        if st.button("Login"):
            try:
                r = requests.post(f"{API_URL}/auth/login", json={"username": user_in, "password": pass_in})
                if r.ok:
                    data = r.json()
                    st.session_state.token = data.get("access_token")
                    st.session_state.role = data.get("role")
                    st.session_state.username = data.get("username")
                    st.success(f"Login como {st.session_state.username} ({st.session_state.role})")
                    st.rerun()
                else:
                    st.error(r.text)
            except Exception as e:
                st.error(f"Erro no login: {e}")
    else:
        st.caption("Sign up disponível apenas para PRODUTOR")
        if st.button("Sign up"):
            try:
                r = requests.post(f"{API_URL}/auth/signup", json={"username": user_in, "password": pass_in})
                if r.ok:
                    st.success("Conta criada. Agora faça login.")
                else:
                    st.error(r.text)
            except Exception as e:
                st.error(f"Erro no signup: {e}")

if st.session_state.token:
    st.sidebar.success(f"Sessão: {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

papel = st.sidebar.radio("Perfil", ["Gestor", "Produtor"], index=(0 if st.session_state.role == "GESTOR" else 1) if st.session_state.role else 1)

# Helpers simples
def _auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def list_fornecedores():
    r = requests.get(f"{API_URL}/fornecedores")
    r.raise_for_status()
    return r.json()

def create_fornecedor(payload):
    r = requests.post(f"{API_URL}/fornecedores", json=payload, headers=_auth_headers())
    r.raise_for_status()
    return r.json()

def patch_aprovacao(fid, aprovado: bool):
    r = requests.patch(
        f"{API_URL}/fornecedores/{fid}/aprovacao",
        json={"aprovado": aprovado},
        headers=_auth_headers(),
    )
    r.raise_for_status()
    return r.json()

def get_ordem():
    r = requests.get(f"{API_URL}/fornecedores/ordem")
    r.raise_for_status()
    return r.json()

if papel == "Produtor":
    if not st.session_state.token:
        st.warning("Autentique-se para submeter inscrição.")
    elif st.session_state.role != "PRODUTOR":
        st.warning("Apenas utilizadores PRODUTOR podem submeter inscrições.")
    else:
        st.header("Inscrição de Produtor")

        nome = st.text_input("Nome do produtor")
        data_inscricao = st.date_input("Data de inscrição", value=date.today())

        st.subheader("Produtos")
        prod_nome = st.text_input("Nome do produto")
        prod_ini = st.date_input("Início intervalo produção", value=date.today())
        prod_fim = st.date_input("Fim intervalo produção", value=date.today())
        capacidade = st.number_input("Capacidade (unidade)", min_value=0, value=0)

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
                novo = create_fornecedor(payload)
                st.success(f"Produtor criado com id {novo['id']} (aguarda aprovação).")
            except Exception as e:
                st.error(f"Erro ao criar fornecedor: {e}")

elif papel == "Gestor":
    st.header("Gestão de Fornecedores")
    if not st.session_state.token:
        st.warning("Autentique-se para gerir fornecedores.")
    elif st.session_state.role != "GESTOR":
        st.warning("Apenas utilizadores GESTOR podem aprovar/reprovar.")
    else:
        if st.button("Recarregar lista"):
            st.rerun()

        fornecedores = list_fornecedores()
        if fornecedores:
            st.subheader("Fornecedores")
            for f in fornecedores:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"#{f['id']} - {f['nome']}")
                    st.caption(
                        f"Data inscrição: {f['data_inscricao']} | "
                        f"Aprovado: {f['aprovado']}"
                    )
                with col2:
                    if not f["aprovado"]:
                        if st.button("Aprovar", key=f"ap_{f['id']}"):
                            patch_aprovacao(f["id"], True)
                            st.rerun()
                with col3:
                    if f["aprovado"]:
                        if st.button("Reprovar", key=f"rp_{f['id']}"):
                            patch_aprovacao(f["id"], False)
                            st.rerun()
        else:
            st.info("Ainda não há fornecedores.")

        st.subheader("Ordem de fornecimento por produto")
        if st.button("Calcular ordem"):
            ordens = get_ordem()
            for o in ordens:
                st.write(
                    f"Produto: {o['produto']} → ordem de fornecedores: "
                    f"{', '.join(map(str, o['fornecedores_ids']))}"
                )