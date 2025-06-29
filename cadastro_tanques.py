# cadastro_tanques.py

import streamlit as st
import pandas as pd
import db_utils

def show():
    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/tanques.png', width=48)
    with col2:
        st.subheader("Cadastro de Tanques")
    
    try:
        df = db_utils.get_data('tbl_tanques')
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        df = pd.DataFrame()
    
    if df.empty:
        df = pd.DataFrame(columns=["tan_id", "tan_nome", "tan_capacidade", "tan_unidade"])
    
    column_config = {
        "tan_id": st.column_config.NumberColumn("ID", disabled=True),
        "tan_nome": st.column_config.TextColumn("Nome*", required=True),
        "tan_capacidade": st.column_config.NumberColumn("Capacidade", format="%.2f"),
        "tan_unidade": st.column_config.TextColumn("Unidade")
    }
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_tbl_tanques"
    )
    
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_tanques"):
            try:
                # Validação
                required_cols = [col for col, config in column_config.items() 
                                if hasattr(config, 'required') and config.required]
                
                missing = False
                for idx, row in edited_df.iterrows():
                    for col in required_cols:
                        if col in row and pd.isna(row[col]):
                            st.warning(f"Linha {idx+1}: Campo '{col}' é obrigatório!")
                            missing = True
                
                if not missing:
                    if db_utils.save_data('tbl_tanques', edited_df):
                        st.success("Dados salvos com sucesso!")
                        st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")
    
    with col2:
        if st.button("🔄 Recarregar", key="btn_recarregar_tbl_tanques"):
            st.session_state.pop("editor_tbl_tanques", None)
            st.rerun()
    
    with col3:
        st.info(f"Tabela: tbl_tanques | Registros: {len(edited_df)}")
