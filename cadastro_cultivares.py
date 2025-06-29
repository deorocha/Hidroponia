# cadastro_cultivares.py

import streamlit as st
import pandas as pd
import db_utils

def show():
    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/cultivares.png', width=48)
    with col2:
        st.subheader("Cadastro de Cultivares")
    
    try:
        df = db_utils.get_data('tbl_cultivares')
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        df = pd.DataFrame()
    
    if df.empty:
        df = pd.DataFrame(columns=[
            "clt_id", "clt_genero_id", "clt_codigo", "clt_nome", 
            "clt_nome_cientifico", "clt_classificacao", "clt_caracteristicas"
        ])
    
    column_config = {
        "clt_id": st.column_config.NumberColumn("ID", disabled=True),
        "clt_genero_id": st.column_config.NumberColumn("Gênero ID", format="%d"),
        "clt_codigo": st.column_config.TextColumn("Código"),
        "clt_nome": st.column_config.TextColumn("Nome"),
        "clt_nome_cientifico": st.column_config.TextColumn("Nome Científico"),
        "clt_classificacao": st.column_config.TextColumn("Classificação"),
        "clt_caracteristicas": st.column_config.TextColumn("Características")
    }
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_tbl_cultivares"
    )
    
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_cultivares"):
            try:
                if db_utils.save_data('tbl_cultivares', edited_df):
                    st.success("Dados salvos com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")
    
    with col2:
        if st.button("🔄 Recarregar", key="btn_recarregar_tbl_cultivares"):
            st.session_state.pop("editor_tbl_cultivares", None)
            st.rerun()
    
    with col3:
        st.info(f"Tabela: tbl_cultivares | Registros: {len(edited_df)}")
