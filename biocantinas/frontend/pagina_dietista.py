import streamlit as st
import requests

def pagina_dietista(API_URL, auth_token):
    st.header("Painel do Dietista")

    st.subheader("Resumo")
    st.write("Esta página é dedicada ao perfil Dietista.")

    # Exemplo: listar fornecedores aprovados
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.get(f"{API_URL}/fornecedores", headers=headers)
        if r.status_code == 200:
            fornecedores = r.json()
            aprovados = [f for f in fornecedores if f.get("aprovado")]
            st.write(f"Fornecedores aprovados: {len(aprovados)}")
            if aprovados:
                with st.expander("Ver lista de aprovados"):
                    for f in aprovados:
                        st.write(f"#{f['id']} - {f['nome']}")
        else:
            st.warning("Não foi possível carregar fornecedores.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

    st.subheader("Planeamento nutricional (placeholder)")
    st.info("Aqui poderá planear menus com base nos produtos disponíveis.")
