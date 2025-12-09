import streamlit as st
import requests
from datetime import date, timedelta

def pagina_dietista(API_URL, auth_token):
    st.header("Painel do Dietista")

    st.subheader("Produtos disponíveis em stock")

    # Listar fornecedores aprovados e seus produtos
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.get(f"{API_URL}/fornecedores", headers=headers)
        if r.status_code == 200:
            fornecedores = r.json()
            aprovados = [f for f in fornecedores if f.get("aprovado")]
            
            if aprovados:
                # Agregar produtos por categoria (tipo)
                produtos_por_categoria = {}
                for fornecedor in aprovados:
                    for produto in fornecedor.get("produtos", []):
                        tipo = produto.get("tipo") or "Sem categoria"
                        nome_produto = produto.get("nome", "Desconhecido")
                        
                        if tipo not in produtos_por_categoria:
                            produtos_por_categoria[tipo] = {}
                        
                        if nome_produto not in produtos_por_categoria[tipo]:
                            produtos_por_categoria[tipo][nome_produto] = []
                        
                        produtos_por_categoria[tipo][nome_produto].append({
                            "fornecedor": fornecedor.get("nome"),
                            "capacidade": produto.get("capacidade", 0),
                            "inicio": produto.get("intervalo_producao_inicio"),
                            "fim": produto.get("intervalo_producao_fim")
                        })
                
                if produtos_por_categoria:
                    st.write(f"Total de categorias: **{len(produtos_por_categoria)}**")
                    
                    # Ícones por tipo
                    icones_tipo = {
                        "fruta": "🍎",
                        "hortícola-folha": "🥬",
                        "hortícola-fruto": "🍅",
                        "tubérculo": "🥕",
                        "proteína": "🥩",
                        "especial": "🍯",
                        "condimento": "🧄",
                        "aromático": "🌿"
                    }
                    
                    # Mostrar produtos organizados por tipo/categoria
                    for tipo in sorted(produtos_por_categoria.keys()):
                        icone = icones_tipo.get(tipo, "📦")
                        produtos_desta_categoria = produtos_por_categoria[tipo]
                        total_produtos = len(produtos_desta_categoria)
                        tipo_titulo = tipo.title() if tipo else "Sem Categoria"
                        
                        with st.expander(f"{icone} {tipo_titulo} ({total_produtos} produtos)"):
                            for produto_nome in sorted(produtos_desta_categoria.keys()):
                                fornecedores_info = produtos_desta_categoria[produto_nome]
                                total_capacidade = sum(f["capacidade"] for f in fornecedores_info)
                                produto_titulo = produto_nome.title() if produto_nome else "Desconhecido"
                                
                                st.markdown(f"**{produto_titulo}** — {total_capacidade} kg disponíveis")
                                
                                for info in fornecedores_info:
                                    st.write(f"  • {info['fornecedor']}: {info['capacidade']} kg")
                                st.write("")  # Espaçamento
                else:
                    st.info("Nenhum produto encontrado nos fornecedores aprovados.")
            else:
                st.info("Nenhum fornecedor aprovado no sistema.")
        else:
            st.warning("Não foi possível carregar fornecedores.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

    st.subheader("Planeamento nutricional")
    st.info("Aqui poderá planear menus com base nos produtos disponíveis acima.")

    headers = {"Authorization": f"Bearer {auth_token}"}

    st.subheader("Gerar ementa automática")
    st.info("ℹ️ A ementa deve começar numa segunda-feira e ser criada com pelo menos 7 dias de antecedência.")
    
    col_data, col_nome = st.columns([1, 2])
    with col_data:
        # Calcular próxima segunda-feira válida (pelo menos 7 dias no futuro)
        hoje = date.today()
        proxima_segunda = hoje + timedelta(days=(7 - hoje.weekday()) % 7 or 7)
        if (proxima_segunda - hoje).days < 7:
            proxima_segunda += timedelta(weeks=1)
        
        data_inicio = st.date_input(
            "Data de início (segunda-feira)",
            value=proxima_segunda,
            min_value=proxima_segunda
        )
    with col_nome:
        nome_ementa = st.text_input(
            "Nome da ementa (opcional)",
            value=f"Ementa semana {data_inicio.isocalendar().week if data_inicio else date.today().isocalendar().week}"
        )
    
    # Validações no frontend
    validacao_ok = True
    if data_inicio.weekday() != 0:
        st.warning("⚠️ A data de início deve ser uma segunda-feira.")
        validacao_ok = False
    
    dias_antecedencia = (data_inicio - hoje).days
    if dias_antecedencia < 7:
        st.warning(f"⚠️ A ementa deve ser criada com pelo menos 7 dias de antecedência (faltam {7 - dias_antecedencia} dias).")
        validacao_ok = False

    if st.button("Gerar ementa", type="primary", disabled=not validacao_ok):
        try:
            resp = requests.post(
                f"{API_URL}/ementas/gerar",
                params={"data_inicio": data_inicio.isoformat(), "nome": nome_ementa or None},
                headers=headers,
            )
            if resp.status_code == 200:
                st.success("Ementa gerada com sucesso!")
                ementa = resp.json()
                st.session_state["ementa_recente"] = ementa
                st.rerun()
            else:
                detail = resp.json().get("detail", "Erro ao gerar ementa")
                st.error(detail)
        except Exception as e:
            st.error(f"Erro ao gerar ementa: {e}")

    if "ementa_recente" in st.session_state:
        ementa = st.session_state["ementa_recente"]
        with st.expander("Ementa gerada agora", expanded=True):
            _render_ementa(ementa, API_URL, headers, idx_render=9999)

    st.subheader("Ementas guardadas")
    try:
        resp_lista = requests.get(f"{API_URL}/ementas/", headers=headers)
        if resp_lista.status_code == 200:
            ementas = resp_lista.json()
            if not ementas:
                st.info("Ainda não existem ementas guardadas.")
            for idx_ementa, ementa in enumerate(sorted(ementas, key=lambda e: e.get("data_inicio", ""))):
                header = f"{ementa.get('nome', 'Ementa')} — {ementa.get('data_inicio', '')} a {ementa.get('data_fim', '')}"
                with st.expander(header, expanded=False):
                    _render_ementa(ementa, API_URL, headers, idx_ementa)
                    cols = st.columns([1, 1, 6])
                    with cols[0]:
                        if st.button("Apagar", key=f"del_{ementa.get('id')}"):
                            del_resp = requests.delete(
                                f"{API_URL}/ementas/{ementa.get('id')}", headers=headers
                            )
                            if del_resp.status_code == 200:
                                st.success("Ementa removida.")
                                st.rerun()
                            elif del_resp.status_code == 404:
                                st.warning("Ementa já não existe.")
                                st.rerun()
                            else:
                                st.error(del_resp.json().get("detail", "Erro ao remover"))
        else:
            st.warning("Não foi possível obter a lista de ementas.")
    except Exception as e:
        st.error(f"Erro ao listar ementas: {e}")


def _render_ementa(ementa: dict, API_URL: str | None = None, headers: dict | None = None, idx_render: int = 0):
    """Mostra refeições agrupadas por dia e permite editar descrição/itens."""
    refeicoes = ementa.get("refeicoes", [])
    if not refeicoes:
        st.write("Sem refeições registadas.")
        return

    dias = {1: "Seg", 2: "Ter", 3: "Qua", 4: "Qui", 5: "Sex"}
    # ordenar por dia e tipo (almoço antes de jantar)
    def _sort_key(r):
        tipo_ord = 0 if str(r.get("tipo", "")).lower() == "almoço" else 1
        return (r.get("dia_semana", 0), tipo_ord)

    refeicoes_ordenadas = []
    for dia, grupo in _group_by_day(refeicoes, key_func=_sort_key).items():
        titulo = dias.get(dia, f"Dia {dia}")
        st.markdown(f"**{titulo}**")
        for idx, refeicao in enumerate(grupo):
            tipo = refeicao.get("tipo", "")
            st.write(f"- {tipo.title()}: {refeicao.get('descricao', '')}")
            itens = refeicao.get("itens", [])
            for item in itens:
                nome = item.get("ingrediente")
                qtd = item.get("quantidade_estimada")
                st.write(f"  • {nome} — {qtd} kg")
            refeicoes_ordenadas.append(refeicao)

    # Bloco de edição detalhada
    if API_URL and headers:
        st.markdown("---")
        st.markdown("**Editar ementa (refeições e itens)**")
        nome_default = ementa.get("nome", "")
        data_inicio_default = ementa.get("data_inicio")
        data_fim_default = ementa.get("data_fim")
        try:
            data_inicio_default = date.fromisoformat(str(data_inicio_default)) if data_inicio_default else date.today()
            data_fim_default = date.fromisoformat(str(data_fim_default)) if data_fim_default else data_inicio_default
        except Exception:
            data_inicio_default = date.today()
            data_fim_default = data_inicio_default

        col1, col2 = st.columns([2, 1])
        novo_nome = col1.text_input("Nome", value=nome_default, key=f"nome_edit_{idx_render}_{ementa.get('id')}")
        nova_data_inicio = col2.date_input("Data início", value=data_inicio_default, key=f"datai_edit_{idx_render}_{ementa.get('id')}")
        nova_data_fim = col2.date_input("Data fim", value=data_fim_default, key=f"dataf_edit_{idx_render}_{ementa.get('id')}")

        edited_refeicoes = []
        for idx, refeicao in enumerate(refeicoes_ordenadas):
            st.markdown(f"**{refeicao.get('tipo','').title()} - Dia {refeicao.get('dia_semana')}**")
            desc = st.text_input(
                "Descrição",
                value=refeicao.get("descricao", ""),
                key=f"desc_{idx_render}_{ementa.get('id')}_{idx}"
            )

            edited_itens = []
            itens = refeicao.get("itens", [])
            for item_idx, item in enumerate(itens):
                col_i1, col_i2 = st.columns([3, 1])
                ing = col_i1.text_input(
                    "Ingrediente",
                    value=item.get("ingrediente", ""),
                    key=f"ing_{idx_render}_{ementa.get('id')}_{idx}_{item_idx}"
                )
                qtd = col_i2.number_input(
                    "Qtd (kg)",
                    min_value=0,
                    value=int(item.get("quantidade_estimada") or 0),
                    key=f"qtd_{idx_render}_{ementa.get('id')}_{idx}_{item_idx}"
                )
                edited_itens.append({
                    "produto_id": item.get("produto_id"),
                    "ingrediente": ing,
                    "quantidade_estimada": int(qtd)
                })

            # Novo item opcional
            col_n1, col_n2 = st.columns([3, 1])
            novo_ing = col_n1.text_input(
                "Novo ingrediente (opcional)",
                value="",
                key=f"novo_ing_{idx_render}_{ementa.get('id')}_{idx}"
            )
            novo_qtd = col_n2.number_input(
                "Qtd nova (kg)",
                min_value=0,
                value=0,
                key=f"novo_qtd_{idx_render}_{ementa.get('id')}_{idx}"
            )
            if novo_ing:
                edited_itens.append({
                    "produto_id": None,
                    "ingrediente": novo_ing,
                    "quantidade_estimada": int(novo_qtd)
                })

            edited_refeicoes.append({
                "dia_semana": refeicao.get("dia_semana"),
                "tipo": refeicao.get("tipo"),
                "descricao": desc,
                "itens": edited_itens,
            })

        if st.button("Guardar alteração", key=f"save_{idx_render}_{ementa.get('id')}"):
            payload = {
                "nome": novo_nome or nome_default,
                "data_inicio": nova_data_inicio.isoformat(),
                "data_fim": nova_data_fim.isoformat(),
                "refeicoes": edited_refeicoes,
            }
            try:
                resp = requests.put(
                    f"{API_URL}/ementas/{ementa.get('id')}",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 200:
                    st.success("Ementa atualizada.")
                    st.rerun()
                elif resp.status_code == 404:
                    st.warning("Ementa não encontrada.")
                    st.rerun()
                else:
                    st.error(resp.json().get("detail", "Erro ao atualizar"))
            except Exception as e:
                st.error(f"Erro ao atualizar ementa: {e}")


def _group_by_day(refeicoes, key_func):
    grouped = {}
    for r in sorted(refeicoes, key=key_func):
        dia = r.get("dia_semana")
        grouped.setdefault(dia, []).append(r)
    return grouped
