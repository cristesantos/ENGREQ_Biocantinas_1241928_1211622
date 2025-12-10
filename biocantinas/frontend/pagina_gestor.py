import streamlit as st
import requests

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

def get_ordem(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores/ordem", headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_gestor(API_URL, auth_token):
    st.header("Gestão de Fornecedores")

    # Criar abas
    tab1, tab2 = st.tabs(["Fornecedores", "Ordem de Fornecimento"])
    
    # Aba 1: Fornecedores
    with tab1:
        if st.button("Recarregar lista"):
            st.rerun()

        fornecedores = list_fornecedores(API_URL, auth_token)
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
                        
                        # Listar produtos
                        produtos = f.get('produtos', [])
                        if produtos:
                            st.write("**Produtos:**")
                            for p in produtos:
                                st.write(f"  • {p['nome']} ({p.get('tipo', 'N/A')}) - Capacidade: {p.get('capacidade', 'N/A')} unidades")
                        else:
                            st.write("Sem produtos cadastrados")
                
                with col2:
                    if not f["aprovado"]:
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
    
    # Aba 2: Ordem de Fornecimento
    with tab2:
        st.subheader("Ordem de fornecimento por produto")

        try:
            fornecedores = list_fornecedores(API_URL, auth_token)
            ordens = get_ordem(API_URL, auth_token)
            
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
            st.error(f"Erro ao carregar ordem: {e.response.status_code} - {e.response.text}")
