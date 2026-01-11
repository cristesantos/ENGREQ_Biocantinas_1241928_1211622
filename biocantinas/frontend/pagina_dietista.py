import streamlit as st
import requests
from datetime import date, timedelta

def pagina_dietista(API_URL, auth_token):
    st.header("Painel do Dietista")

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
                unidade = item.get("unidade_medida") or "kg"
                st.write(f"  • {nome} — {qtd} {unidade}")
            refeicoes_ordenadas.append(refeicao)

    # Bloco de edição detalhada com seleção de receita
    if API_URL and headers:
        st.markdown("---")
        st.markdown("**Editar ementa (selecionando receitas do catálogo)**")
        nome_default = ementa.get("nome", "")
        data_inicio_default = ementa.get("data_inicio")
        data_fim_default = ementa.get("data_fim")
        try:
            data_inicio_default = date.fromisoformat(str(data_inicio_default)) if data_inicio_default else date.today()
            data_fim_default = date.fromisoformat(str(data_fim_default)) if data_fim_default else data_inicio_default
        except Exception:
            data_inicio_default = date.today()
            data_fim_default = data_inicio_default

        # Determinar semana ISO para filtrar receitas disponíveis
        semana_ementa = data_inicio_default.isocalendar()[1]

        # Carregar receitas disponíveis para a semana
        receitas_disponiveis = []
        try:
            resp_rec = requests.get(
                f"{API_URL}/receitas/disponiveis",
                params={"semana": semana_ementa},
                headers=headers,
            )
            if resp_rec.status_code == 200:
                receitas_disponiveis = resp_rec.json()
            else:
                st.warning("Não foi possível carregar receitas disponíveis para a semana.")
        except Exception as e:
            st.error(f"Erro ao carregar receitas disponíveis: {e}")

        receitas_por_id = {r["id"]: r for r in receitas_disponiveis}

        col1, col2 = st.columns([2, 1])
        novo_nome = col1.text_input("Nome", value=nome_default, key=f"nome_edit_{idx_render}_{ementa.get('id')}")
        nova_data_inicio = col2.date_input("Data início", value=data_inicio_default, key=f"datai_edit_{idx_render}_{ementa.get('id')}")
        nova_data_fim = col2.date_input("Data fim", value=data_fim_default, key=f"dataf_edit_{idx_render}_{ementa.get('id')}")

        edited_refeicoes = []
        for idx, refeicao in enumerate(refeicoes_ordenadas):
            st.markdown(f"**{refeicao.get('tipo','').title()} - Dia {refeicao.get('dia_semana')}**")

            # Filtrar receitas pelo tipo
            tipo_ref = refeicao.get("tipo")
            receitas_tipo = [r for r in receitas_disponiveis if r.get("tipo_refeicao") in [tipo_ref, "ambos"]]
            receita_atual_id = refeicao.get("receita_id")

            # Se a receita atual não estiver na lista de disponíveis, adicionar opção e avisar
            receita_atual_obj = None
            if receita_atual_id:
                receita_atual_obj = next((r for r in receitas_disponiveis if r.get("id") == receita_atual_id), None)
                if not receita_atual_obj and refeicao.get("descricao"):
                    receitas_tipo.append({
                        "id": receita_atual_id,
                        "nome": refeicao.get("descricao"),
                        "categoria": "(fora da disponibilidade)",
                        "tipo_refeicao": tipo_ref,
                        "ingredientes": refeicao.get("itens", []),
                    })
                    st.warning("A receita atualmente selecionada não está disponível para esta semana. Escolha outra receita ou mantenha ciente da indisponibilidade.")

            options = {f"{r['nome']} ({r.get('categoria','')})": r["id"] for r in receitas_tipo}
            label_default = None
            if receita_atual_id and receita_atual_id in options.values():
                for k, v in options.items():
                    if v == receita_atual_id:
                        label_default = k
                        break

            selected_label = st.selectbox(
                "Receita",
                list(options.keys()) or ["Nenhuma receita disponível para o tipo"],
                index=list(options.keys()).index(label_default) if label_default else 0,
                key=f"rec_sel_{idx_render}_{ementa.get('id')}_{idx}"
            ) if options else None

            receita_escolhida = receitas_por_id.get(options[selected_label]) if (options and selected_label) else None

            itens_finais = []
            desc = refeicao.get("descricao", "")
            if receita_escolhida:
                desc = receita_escolhida.get("nome", desc)
                for ing in receita_escolhida.get("ingredientes", []):
                    unidade = ing.get("unidade_medida") or "kg"
                    qty = ing.get("quantidade_por_porcao") or 0
                    itens_finais.append({
                        "produto_id": None,
                        "ingrediente": ing.get("produto_nome"),
                        "quantidade_estimada": qty,
                        "unidade_medida": unidade
                    })
            else:
                # fallback aos itens atuais
                for item in refeicao.get("itens", []):
                    itens_finais.append({
                        "produto_id": item.get("produto_id"),
                        "ingrediente": item.get("ingrediente"),
                        "quantidade_estimada": item.get("quantidade_estimada"),
                        "unidade_medida": item.get("unidade_medida")
                    })

            st.caption("Ingredientes (quantidades finais da receita)")
            for item in itens_finais:
                st.write(f"  • {item['ingrediente']}: {item['quantidade_estimada']} {item.get('unidade_medida') or 'kg'}")

            edited_refeicoes.append({
                "dia_semana": refeicao.get("dia_semana"),
                "tipo": refeicao.get("tipo"),
                "descricao": desc,
                "itens": itens_finais,
                "receita_id": receita_escolhida.get("id") if receita_escolhida else None,
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
