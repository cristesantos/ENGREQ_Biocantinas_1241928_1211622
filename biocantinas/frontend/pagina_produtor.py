import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd

def create_fornecedor(API_URL, auth_token, payload):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.post(f"{API_URL}/fornecedores", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_produtor(API_URL, auth_token):
    st.header("Área do Produtor")
    
    # ============ PREVISÃO DE NECESSIDADES ============
    st.subheader("🔍 Previsão de Necessidades")
    st.write("Visualize as necessidades previstas de produtos para planejamento")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input(
            "Data Início",
            value=date.today(),
            key="preview_inicio"
        )
    with col2:
        data_fim = st.date_input(
            "Data Fim",
            value=date.today() + timedelta(days=7),
            key="preview_fim"
        )
    
    if st.button("🔍 Ver Previsão", key="btn_preview"):
        try:
            response = requests.get(
                f"{API_URL}/aprovisionamento/preview",
                params={
                    "data_inicio": str(data_inicio),
                    "data_fim": str(data_fim)
                },
                headers=headers
            )
            
            if response.status_code == 200:
                dados = response.json()
                
                st.success(f"✅ Previsão gerada para {dados['periodo']}")
                
                # Linha 1: Ementa e Necessidades Planejadas lado a lado
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📋 Ementa do Período**")
                    if dados.get("refeicoes_detalhes"):
                        ementa_html = "<div style='font-size: 0.85em; line-height: 1.3;'>"
                        for refeicao in dados["refeicoes_detalhes"]:
                            data_label = refeicao.get('data', '')
                            dia_semana = refeicao.get('dia_semana', '')
                            ementa_html += f"<p style='margin: 8px 0 2px 0;'><b>📅 {data_label} ({dia_semana}) - {refeicao['tipo'].title()}</b><br>"
                            ementa_html += f"<i>{refeicao['descricao']}</i></p>"
                            ementa_html += "<ul style='margin: 2px 0 8px 0; padding-left: 20px;'>"
                            for ing in refeicao['ingredientes']:
                                ementa_html += f"<li>{ing['ingrediente']}: {ing['quantidade']} kg</li>"
                            ementa_html += "</ul><hr style='margin: 4px 0;'>"
                        ementa_html += "</div>"
                        st.markdown(ementa_html, unsafe_allow_html=True)
                    else:
                        st.info("Sem ementas")
                
                with col2:
                    st.markdown("**📊 Necessidades Planejadas**")
                    st.caption("Quantidade total de produtos com histórico aplicado")
                    if dados.get("necessidades_previstas_historico"):
                        df_planejadas = pd.DataFrame(
                            list(dados["necessidades_previstas_historico"].items()),
                            columns=["Produto", "Quantidade (kg)"]
                        )
                        st.dataframe(df_planejadas, use_container_width=True)
                    else:
                        st.info("Sem histórico")
                
                st.divider()
                
                # Linha 2: Histórico de Reservas (largura total)
                st.markdown("**📈 Histórico de Reservas**")
                st.caption("Dados históricos por prato do período")
                if dados.get("historico_detalhes"):
                    df_historico = pd.DataFrame(dados["historico_detalhes"])
                    # Calcular altura baseada no número de refeições
                    num_refeicoes = len(dados.get("refeicoes_detalhes", []))
                    altura_historico = min(max(num_refeicoes * 35 + 38, 150), 400)
                    
                    # Aplicar CSS para reduzir tamanho da fonte e padding
                    st.markdown("""
                    <style>
                    [data-testid="stDataFrame"] {
                        font-size: 0.8em;
                    }
                    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
                        padding: 4px 8px !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    st.dataframe(df_historico, use_container_width=True, height=altura_historico)
                else:
                    st.info("Sem dados históricos")
            
            else:
                st.error(f"❌ Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
        
        except Exception as e:
            st.error(f"❌ Erro ao conectar com API: {str(e)}")
