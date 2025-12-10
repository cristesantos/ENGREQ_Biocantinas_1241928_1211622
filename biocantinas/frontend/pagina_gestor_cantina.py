import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

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

def get_preview_aprovisionamento(API_URL, auth_token, data_inicio, data_fim):
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"data_inicio": data_inicio, "data_fim": data_fim}
    r = requests.get(f"{API_URL}/aprovisionamento/preview", headers=headers, params=params)
    r.raise_for_status()
    return r.json()

def pagina_gestor_cantina(API_URL, auth_token):
    st.header("Gestão da Cantina")
    
    # Criar abas
    tab1, tab2 = st.tabs(["Plano de Produção", "Alertas"])
    
    # Aba 1: Plano de Produção
    with tab1:
        st.subheader("Plano de Produção")
        st.write("Comparação entre previsão histórica e reservas reais")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(
                "Data Início",
                value=date.today(),
                key="plan_inicio"
            )
        with col2:
            data_fim = st.date_input(
                "Data Fim",
                value=date.today() + timedelta(days=6),
                key="plan_fim"
            )
        
        if st.button("📊 Ver Planejamento"):
            try:
                dados = get_preview_aprovisionamento(
                    API_URL, auth_token, 
                    data_inicio.isoformat(), 
                    data_fim.isoformat()
                )
                
                st.success(f"✅ Planejamento gerado para {dados['periodo']}")
                
                # Mostrar resumo das refeições
                if dados.get('refeicoes_detalhes'):
                    col_titulo, col_header_qtd = st.columns([3, 1])
                    with col_titulo:
                        st.markdown("<h3 style='text-align: center;'>Resumo das Refeições</h3>", unsafe_allow_html=True)
                    with col_header_qtd:
                        st.markdown("<h3 style='text-align: center;'>Produzir</h3>", unsafe_allow_html=True)
                    
                    for ref in dados['refeicoes_detalhes']:
                        # Calcula quantidade a produzir
                        qtd_produzir = ref.get('reservas_reais', 0)
                        if qtd_produzir == 0 and ref.get('previsao_reservas'):
                            qtd_produzir = ref['previsao_reservas']
                        
                        col_expander, col_qtd = st.columns([3, 1])
                        
                        with col_expander:
                            with st.expander(f"{ref['dia_nome']} ({ref['data']}) - {ref['tipo']}: {ref['descricao']}"):
                                st.write(f"**Dia da semana:** {ref['dia_semana_texto']}")
                                
                                # Previsão histórica
                                if ref.get('previsao_reservas'):
                                    st.write(f"**Previsão (histórico):** {ref['previsao_reservas']} refeições")
                                
                                # Reservas reais
                                if ref.get('reservas_reais') is not None:
                                    st.write(f"**Reservas reais:** {ref['reservas_reais']} refeições")
                                    
                                    # Comparação
                                    if ref.get('previsao_reservas'):
                                        dif = ref['reservas_reais'] - ref['previsao_reservas']
                                        perc = (dif / ref['previsao_reservas'] * 100) if ref['previsao_reservas'] > 0 else 0
                                        if abs(dif) > 0:
                                            st.write(f"**Diferença:** {dif:+.0f} ({perc:+.1f}%)")
                                else:
                                    st.info("Sem reservas reais ainda")
                                
                                # Ingredientes
                                if ref.get('ingredientes'):
                                    st.write("**Ingredientes:**")
                                    for ing in ref['ingredientes']:
                                        st.write(f"  • {ing['ingrediente']}: {ing['quantidade_estimada']} unidades")
                        
                        with col_qtd:
                            st.markdown(f"<div style='display: flex; align-items: center; justify-content: center; height: 48px; font-size: 20px; font-weight: bold;'>{qtd_produzir}</div>", unsafe_allow_html=True)
                
            except requests.exceptions.HTTPError as e:
                st.error(f"Erro ao gerar planejamento: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")
    
    # Aba 2: Alertas
    with tab2:
        st.subheader("⚠️ Alertas de Desvio > 10%")
        st.write("Refeições com desvio significativo entre reservas reais e previsão histórica")
        
        try:
            # Buscar dados de todas as ementas disponíveis (últimos 30 dias até 30 dias futuros)
            data_inicio_alerta = date.today() - timedelta(days=30)
            data_fim_alerta = date.today() + timedelta(days=30)
            
            dados = get_preview_aprovisionamento(
                API_URL, auth_token,
                data_inicio_alerta.isoformat(),
                data_fim_alerta.isoformat()
            )
            
            # Calcular alertas a partir das refeições
            alertas = []
            for ref in dados.get('refeicoes_detalhes', []):
                previsao = ref.get('previsao_reservas') or 0
                real = ref.get('reservas_reais') or 0
                
                # Só calcular desvio se ambos os valores forem válidos e maiores que zero
                if previsao > 0 and real > 0:
                    desvio = ((real - previsao) / previsao) * 100
                    
                    if abs(desvio) > 10:
                        alertas.append({
                            "Data": ref['data'],
                            "Dia": ref['dia_nome'],
                            "Tipo": ref['tipo'].title(),
                            "Refeição": ref['descricao'],
                            "Previsão": previsao,
                            "Reservas Reais": real,
                            "Desvio (%)": f"{desvio:+.1f}%"
                        })
            
            if alertas:
                st.warning(f"⚠️ **{len(alertas)} alertas encontrados**")
                df_alertas = pd.DataFrame(alertas)
                st.dataframe(df_alertas, use_container_width=True)
            else:
                st.success("✅ Nenhum alerta de desvio > 10% encontrado")
        
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao carregar alertas: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"Erro: {str(e)}")
