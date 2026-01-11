"""
Página para gestão do catálogo de receitas
"""
import streamlit as st
import requests
import pandas as pd
from datetime import date


def pagina_gestao_receitas(API_URL, auth_token):
    """Interface para gestão de receitas"""
    st.header("🍽️ Catálogo de Receitas")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs([
        "📖 Ver Receitas",
        "➕ Criar Receita",
        "✏️ Editar Receita"
    ])
    
    # ============ TAB 1: VER RECEITAS ============
    with tab1:
        st.subheader("Receitas Disponíveis")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_tipo = st.selectbox(
                "Filtrar por tipo de refeição",
                ["Todas", "almoço", "jantar", "ambos"]
            )
        with col2:
            apenas_ativas = st.checkbox("Apenas ativas", value=True)
        
        try:
            # Listar receitas
            url = f"{API_URL}/receitas"
            params = {}
            if not apenas_ativas:
                params["apenas_ativas"] = False
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                receitas = response.json()
                
                # Filtrar por tipo se necessário
                if filtro_tipo != "Todas":
                    receitas = [r for r in receitas if r.get("tipo_refeicao") in [filtro_tipo, "ambos"]]
                
                if receitas:
                    # Criar DataFrame
                    df_data = []
                    for receita in receitas:
                        df_data.append({
                            "ID": receita.get("id"),
                            "Nome": receita.get("nome"),
                            "Tipo": receita.get("tipo_refeicao", "N/D"),
                            "Categoria": receita.get("categoria", "N/D"),
                            "Tempo (min)": receita.get("tempo_preparo", "-"),
                            "Ingredientes": len(receita.get("ingredientes", [])),
                            "Ativa": "✅" if receita.get("ativa") else "❌"
                        })
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Detalhes de cada receita
                    st.divider()
                    st.subheader("Detalhes das Receitas")
                    
                    for receita in receitas:
                        with st.expander(f"🍽️ {receita['nome']} ({receita['categoria']})"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Tipo:** {receita.get('tipo_refeicao', 'N/D')}")
                            with col2:
                                st.write(f"**Categoria:** {receita.get('categoria', 'N/D')}")
                            with col3:
                                st.write(f"**Tempo:** {receita.get('tempo_preparo', '-')} min")
                            
                            if receita.get('descricao'):
                                st.write(f"**Descrição:** {receita['descricao']}")
                            
                            st.write("**Ingredientes (quantidade final da receita):**")
                            for ing in receita.get("ingredientes", []):
                                unidade = ing.get("unidade_medida") or "kg"
                                st.write(f"  • {ing['produto_nome']}: {ing['quantidade_por_porcao']} {unidade}")
                else:
                    st.info("Nenhuma receita encontrada")
            else:
                st.error(f"Erro ao carregar receitas: {response.status_code}")
        
        except Exception as e:
            st.error(f"Erro ao listar receitas: {e}")
    
    # ============ TAB 2: CRIAR RECEITA ============
    with tab2:
        st.subheader("Criar Nova Receita")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome da Receita *", placeholder="ex: Bacalhau à Brás")
            tipo_refeicao = st.selectbox("Tipo de Refeição *", ["almoço", "jantar", "ambos"])
        with col2:
            categoria = st.text_input("Categoria *", placeholder="ex: peixe, carne, vegetariano")
        
        descricao = st.text_area("Descrição", placeholder="Descrição breve da receita")
        tempo_preparo = st.number_input("Tempo de Preparo (minutos)", value=0, min_value=0)
        
        st.markdown("---")
        st.subheader("Ingredientes")
        
        # Formulário para adicionar ingredientes
        ingredientes = []
        num_ingredientes = st.number_input("Número de ingredientes", value=3, min_value=1, max_value=20)
        
        cols = st.columns(3)
        for i in range(int(num_ingredientes)):
            with cols[i % 3]:
                st.write(f"**Ingrediente {i+1}**")
        
        # Listar produtos disponíveis
        try:
            resp_prods = requests.get(f"{API_URL}/produtos-catalogo", headers=headers)
            if resp_prods.status_code == 200:
                produtos_disponiveis = resp_prods.json()
                nomes_produtos = [p["nome"] for p in produtos_disponiveis]
            else:
                nomes_produtos = []
        except:
            nomes_produtos = []
        
        # Adicionar campos de ingredientes dinamicamente
        for i in range(int(num_ingredientes)):
            col_prod, col_qtd, col_unit = st.columns([2, 1, 1])
            
            with col_prod:
                if nomes_produtos:
                    produto_nome = st.selectbox(
                        f"Produto {i+1}",
                        nomes_produtos,
                        key=f"prod_{i}"
                    )
                else:
                    produto_nome = st.text_input(f"Produto {i+1}", key=f"prod_{i}")
                
                # Buscar ID do produto
                if nomes_produtos and produto_nome:
                    produto_id = next(
                        (p["id"] for p in produtos_disponiveis if p["nome"] == produto_nome),
                        None
                    )
                else:
                    produto_id = None
            
            with col_qtd:
                quantidade = st.number_input(
                    f"Qtd",
                    value=0.1,
                    min_value=0.01,
                    step=0.1,
                    key=f"qty_{i}"
                )

            with col_unit:
                unidade = st.selectbox(
                    "Unidade",
                    ["kg", "unidades", "L"],
                    index=0 if (produtos_disponiveis and produto_nome and next((p.get("unidade_medida") for p in produtos_disponiveis if p.get("nome") == produto_nome), "kg") == "kg") else 0,
                    key=f"unit_{i}"
                )
            
            if produto_nome and produto_id:
                ingredientes.append({
                    "produto_catalogo_id": produto_id,
                    "produto_nome": produto_nome,
                    "quantidade_por_porcao": quantidade,
                    "unidade_medida": unidade
                })
        
        st.markdown("---")
        
        if st.button("💾 Criar Receita", type="primary"):
            if not nome or not categoria or not ingredientes:
                st.error("Preencha todos os campos obrigatórios e adicione ingredientes")
            else:
                try:
                    payload = {
                        "nome": nome,
                        "descricao": descricao,
                        "tipo_refeicao": tipo_refeicao,
                        "categoria": categoria,
                        "tempo_preparo": int(tempo_preparo) if tempo_preparo > 0 else None,
                        "ativa": True,
                        "ingredientes": ingredientes
                    }
                    
                    response = requests.post(
                        f"{API_URL}/receitas",
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        st.success(f"✅ Receita '{nome}' criada com sucesso!")
                        st.rerun()
                    else:
                        detail = response.json().get("detail", "Erro ao criar receita")
                        st.error(f"❌ {detail}")
                
                except Exception as e:
                    st.error(f"❌ Erro ao criar receita: {e}")
    
    # ============ TAB 3: EDITAR RECEITA ============
    with tab3:
        st.subheader("Editar/Remover Receita")
        
        try:
            response = requests.get(f"{API_URL}/receitas", headers=headers)
            
            if response.status_code == 200:
                receitas = response.json()
                
                if receitas:
                    receita_selecionada_nome = st.selectbox(
                        "Selecionar Receita",
                        [r["nome"] for r in receitas]
                    )
                    
                    receita_selecionada = next(
                        r for r in receitas if r["nome"] == receita_selecionada_nome
                    )
                    
                    st.info(f"ID: {receita_selecionada['id']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🗑️ Remover Receita", key="delete_btn"):
                            try:
                                del_response = requests.delete(
                                    f"{API_URL}/receitas/{receita_selecionada['id']}",
                                    headers=headers
                                )
                                
                                if del_response.status_code in [200, 204]:
                                    st.success("✅ Receita removida")
                                    st.rerun()
                                else:
                                    st.error("Erro ao remover receita")
                            except Exception as e:
                                st.error(f"Erro: {e}")
                    
                    with col2:
                        st.info("Funcionalidade de edição em desenvolvimento")
                    
                    # Mostrar detalhes
                    st.divider()
                    st.subheader("Detalhes da Receita")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Tipo:** {receita_selecionada['tipo_refeicao']}")
                    with col2:
                        st.write(f"**Categoria:** {receita_selecionada['categoria']}")
                    with col3:
                        st.write(f"**Status:** {'✅ Ativa' if receita_selecionada['ativa'] else '❌ Inativa'}")
                    
                    st.write(f"**Descrição:** {receita_selecionada.get('descricao', '-')}")
                    st.write(f"**Tempo de Preparo:** {receita_selecionada.get('tempo_preparo', '-')} minutos")
                    
                    st.write("**Ingredientes (quantidade final da receita):**")
                    for ing in receita_selecionada.get("ingredientes", []):
                        unidade = ing.get("unidade_medida") or "kg"
                        st.write(f"  • {ing['produto_nome']}: {ing['quantidade_por_porcao']} {unidade}")
                else:
                    st.info("Nenhuma receita cadastrada")
        
        except Exception as e:
            st.error(f"Erro ao carregar receitas: {e}")
