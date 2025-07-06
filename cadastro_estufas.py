# cadastro_estufas.py

import streamlit as st
import pandas as pd
import db_utils
import sqlite3

def show():
    # Verificar/criar tabela se não existir
    try:
        conn = sqlite3.connect('./dados/hidroponia.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tbl_estufas (
                est_id INTEGER PRIMARY KEY AUTOINCREMENT,
                est_codigo TEXT NOT NULL,
                est_descricao TEXT
            )
        ''')
        conn.commit()
    except Exception as e:
        st.error(f"Erro ao verificar/criar tabela: {str(e)}")
    finally:
        if conn:
            conn.close()

    col1, col2 = st.columns([10, 200])
    with col1:
        st.image('./imagens/estufas.png', width=48)
    with col2:
        st.subheader("Cadastro de Estufas")
    
    try:
        df = db_utils.get_data('tbl_estufas')
        if df.empty:
            df = pd.DataFrame(columns=["est_id", "est_codigo", "est_descricao"])
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        df = pd.DataFrame(columns=["est_id", "est_codigo", "est_descricao"])
    
    # Garantir tipos de dados corretos
    for col in ["est_id"]:
        if col in df.columns and df[col].dtype != 'Int64':
            df[col] = df[col].astype('Int64')
    
    column_config = {
        "est_id": st.column_config.NumberColumn("ID", disabled=True),
        "est_codigo": st.column_config.TextColumn("Código*", required=True),
        "est_descricao": st.column_config.TextColumn("Descrição")
    }
    
    # Garantir que temos as colunas esperadas
    for col in column_config.keys():
        if col not in df.columns:
            df[col] = None
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_tbl_estufas"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_estufas"):
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
                
                # Verificar códigos duplicados
                duplicates = edited_df['est_codigo'].duplicated()
                if duplicates.any():
                    dup_codes = edited_df[duplicates]['est_codigo'].unique()
                    st.warning(f"Códigos duplicados encontrados: {', '.join(dup_codes)}")
                    missing = True
                
                if not missing:
                    try:
                        # Garantir que IDs não sejam alterados
                        if 'est_id' in edited_df.columns:
                            edited_df['est_id'] = edited_df['est_id'].astype('Int64')
                        
                        db_utils.save_data('tbl_estufas', edited_df)
                        st.success("Dados salvos com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {str(e)}")
            except Exception as e:
                st.error(f"Erro ao validar: {str(e)}")
    
    with col2:
        if st.button("🔄 Recarregar", key="btn_recarregar_tbl_estufas"):
            st.session_state.pop("editor_tbl_estufas", None)
            st.rerun()
    
    with col3:
        st.info(f"Tabela: tbl_estufas | Registros: {len(edited_df)}")
