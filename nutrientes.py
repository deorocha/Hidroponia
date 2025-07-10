# nutrientes.py

import streamlit as st
import sqlite3
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import numpy as np

# Configuração inicial da página
st.set_page_config(
    page_title="Nutrientes",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': None, 'Get help': None, 'Report a bug': None}
)

DB_NAME = "./dados/hidroponia.db"

@st.cache_data
def load_culturas():
    """Carrega dados do banco com cache"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT clt_id, clt_nome FROM tbl_cultivares ORDER BY clt_nome")
        cultivare = cursor.fetchall()
        
        # Processar dados
        data = {'cultivares': cultivare}
        return data
    except Exception as e:
        st.error(f"Erro no banco: {str(e)}")
        return {k: [] for k in ['cultivares']}

@st.cache_data
def load_culturas_nutrientes(cultivar_id):
    """Carrega os dados de nutrientes para uma cultivar específica"""
    try:
        conn = sqlite3.connect(DB_NAME)
        query = """
        SELECT 
            cn.cnu_id,
            cn.cnu_cultura_id,
            cn.cnu_etapa_producao_id,
            cn.cnu_nutriente_id,
            n.nut_nome,
            n.nut_simbolo,
            n.nut_genero_id,
            cn.cnu_valor_minimo,
            cn.cnu_valor_medio,
            cn.cnu_valor_maximo,
            cn.cnu_referencia,
            cn.cnu_observacao
        FROM tbl_culturas_nutrientes cn
        JOIN tbl_nutrientes n ON cn.cnu_nutriente_id = n.nut_id
        WHERE cn.cnu_cultura_id = ?
        ORDER BY cn.cnu_nutriente_id
        """
        df = pd.read_sql_query(query, conn, params=(cultivar_id,))
        
        # Apenas converter para float (sem alterar escala)
        if not df.empty:
            valor_cols = [
                'cnu_valor_minimo', 
                'cnu_valor_medio', 
                'cnu_valor_maximo'
            ]
            
            # Converter colunas para float
            for col in valor_cols:
                df[col] = df[col].astype(float)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar nutrientes: {str(e)}")
        return pd.DataFrame()

def main():
    # Sidebar (menu)
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>🧬 Nutrientes</h2>",
                    unsafe_allow_html=True)

        st.markdown("---")
        
        dados_cultivares = load_culturas()
        
        # Criar lista de nomes e dicionário de mapeamento nome->ID
        nomes_cultivares = []
        cultivar_id_map = {}
        
        for cultivar in dados_cultivares["cultivares"]:
            clt_id = cultivar[0]
            clt_nome = cultivar[1]
            nomes_cultivares.append(clt_nome)
            cultivar_id_map[clt_nome] = clt_id

        cultivar_nome = st.selectbox('Selecione uma cultivar:', options=nomes_cultivares)
        
        # Obter ID correspondente ao nome selecionado
        cultivar_id = cultivar_id_map.get(cultivar_nome, None)

        nomes_sistemas = ["NFT", "DFT", "DWC", "Gotejamento", "Subirrigação", "Aeroponia", "Pavio", "Fluxo e Refluxo", "Aquaponia", "Substrato"]
        nomes_etapas = ["Germinação", "Berçário", "Crescimento", "Fase final"]
        sistema_producao = st.selectbox('Selecione um Sistema:', options=nomes_sistemas, index=0)
        etapa_producao = st.selectbox('Selecione a Etapa:', options=nomes_etapas, index=2)

        # Adiciona espaço para empurrar os botões para o rodapé
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Rodapé do sidebar com os botões
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", key="btn_back_nutrientes", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_nutrientes", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

    # Área principal - Dados dos nutrientes
    if cultivar_id:
        # Carregar dados dos nutrientes para a cultivar selecionada
        df_nutrientes = load_culturas_nutrientes(cultivar_id)
        
        if not df_nutrientes.empty:
            st.write(f"Recomendações de Nutrientes para :red[{cultivar_nome}]")

            # Combinar nome e símbolo em uma única coluna
            df_nutrientes['Nutriente'] = df_nutrientes['nut_nome'] + " (" + df_nutrientes['nut_simbolo'] + ")"
            
            # Renomear colunas para português
            df_display = df_nutrientes.rename(columns={
                'cnu_nutriente_id': 'Id',
                'cnu_valor_minimo': 'Mínimo',
                'cnu_valor_medio': 'Médio',
                'cnu_valor_maximo': 'Máximo',
                'cnu_referencia': 'Fonte',
                'cnu_observacao': 'Observação',
                'nut_genero_id': 'Tipo'
            })
            
            # Selecionar colunas relevantes para exibição
            df_display = df_display[[
                'Id', 'Nutriente', 'Mínimo', 'Médio', 'Máximo', 'Fonte', 'Observação', 'Tipo'
            ]]
            
            # Configurar AgGrid
            gb = GridOptionsBuilder.from_dataframe(df_display)
            
            # Configurar colunas
            gb.configure_columns(['Id'], width=50, type=["numericColumn"])
            gb.configure_columns(['Nutriente'], width=150)
            gb.configure_columns(['Mínimo', 'Médio', 'Máximo'], width=100, type=["numericColumn"])
            gb.configure_columns(['Fonte'], width=150)
            gb.configure_columns(['Observação'], width=300)
            
            # ADICIONADO: Ocultar coluna Tipo
            gb.configure_column('Tipo', hide=True)  # Esta linha oculta a coluna Tipo

            # CORREÇÃO: Usando JsCode para cellStyle
            cell_style_jscode = JsCode("""
                function(params) {
                    if (params.data.Tipo === 1) {
                        return {backgroundColor: '#ECF5E7'};
                    } else if (params.data.Tipo === 2) {
                        return {backgroundColor: '#ECF4FA'};
                    }
                    return null;
                }
            """)

            # Configurar estilo condicional para todas as colunas
            for col in ['Id', 'Nutriente', 'Mínimo', 'Médio', 'Máximo', 'Fonte', 'Observação']:
                gb.configure_column(
                    col, 
                    cellStyle=cell_style_jscode
                )
            
            # Configurar cabeçalho
            gb.configure_default_column(
                resizable=True,
                filterable=True,
                sortable=True,
                editable=False,
                wrapText=True
            )
            
            # Configurar estilo do cabeçalho
            grid_options = gb.build()
            grid_options['headerHeight'] = 30
            grid_options['rowHeight'] = 30
            
            # Adicionar estilo para o cabeçalho
            grid_options['defaultColDef'] = {
                'headerClass': 'header-class'
            }
            
            # CSS para cabeçalho
            st.markdown("""
            <style>
                .header-class {
                    background-color: #FFF5D9 !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Exibir a tabela
            AgGrid(
                df_display,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.NO_UPDATE,
                fit_columns_on_grid_load=True,
                height=600,
                theme='streamlit',
                allow_unsafe_jscode=True
            )
            
        else:
            st.warning("Nenhum dado de nutriente encontrado para esta cultivar.")
    else:
        st.warning("Selecione uma cultivar válida para visualizar os nutrientes.")

if __name__ == "__main__":
    main()
