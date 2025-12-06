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
#  6. Sidebar e navegação
# ============================================================

st.sidebar.title("BioCantinas")
pagina = st.sidebar.radio("Perfil", ["Página inicial", "Gestor", "Produtor"])


# ============================================================
#  7. Página inicial
# ============================================================

if pagina == "Página inicial":
    st.header("Bem-vindo ao BioCantinas!")
    st.write("Selecione uma opção na barra lateral.")


# ============================================================
#  8. Páginas importadas
# ============================================================

elif pagina == "Gestor":
    from pagina_gestor import pagina_gestor
    pagina_gestor(API_URL)

elif pagina == "Produtor":
    from pagina_produtor import pagina_produtor
    pagina_produtor(API_URL)
