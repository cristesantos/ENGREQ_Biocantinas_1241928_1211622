import streamlit as st
import requests

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

def pagina_gestor_cantina(API_URL, auth_token):
    st.header("Aprovisionamento de Produtos")

    st.subheader("Ordem de fornecimento por produto")

    # Usar st.cache_data com um parâmetro de versão para forçar recarregamento
    @st.cache_data(show_spinner=True, ttl=60)
    def carregar_dados():
        ordens = get_ordem(API_URL, auth_token)
        fornecedores = list_fornecedores(API_URL, auth_token)
        return ordens, fornecedores

    try:
        ordens, fornecedores = carregar_dados()
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
    except requests.exceptions.HTTPError as e:
        st.error(f"Erro ao carregar ordens: {e.response.status_code} - {e.response.text}")
