# cadastro_nutrientes.py

import streamlit as st
import pandas as pd
import db_utils

def show():
    generos = db_utils.get_generos_nutrientes()
    
    # Cria mapeamentos
    id_to_desc = {id: desc for id, desc in generos}
    desc_to_id = {desc: id for id, desc in generos}
    opcoes = [desc for id, desc in generos] if generos else []
    
    # Carrega dados
    try:
        df = db_utils.get_data('tbl_nutrientes')
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        df = pd.DataFrame()
    
    # Converte IDs para descrições
    if not df.empty:
        df['nut_genero_desc'] = df['nut_genero_id'].apply(
            lambda x: id_to_desc.get(x, None) if pd.notna(x) else None
        )
    else:
        df = pd.DataFrame(columns=[
            'nut_id', 'nut_codigo', 'nut_nome', 'nut_simbolo', 
            'nut_genero_id', 'nut_genero_desc', 'nut_funcao', 
            'nut_carencia', 'nut_excesso', 'nut_massa_atomica', 'nut_unidade_id'
        ])
    
    # Ordem das colunas solicitada
    ordem_colunas = [
        'nut_id', 
        'nut_codigo', 
        'nut_nome', 
        'nut_simbolo', 
        'nut_genero_id', 
        'nut_genero_desc', 
        'nut_funcao', 
        'nut_carencia', 
        'nut_excesso', 
        'nut_massa_atomica', 
        'nut_unidade_id'
    ]
    
    # Mantém apenas colunas existentes na ordem especificada
    df = df[[col for col in ordem_colunas if col in df.columns]]
    
    # Configuração das colunas
    column_config = {
        "nut_id": st.column_config.NumberColumn("ID", disabled=True),
        "nut_codigo": st.column_config.TextColumn("Código"),
        "nut_nome": st.column_config.TextColumn("Nome*", required=True),
        "nut_simbolo": st.column_config.TextColumn("Símbolo"),
        "nut_massa_atomica": st.column_config.NumberColumn("Massa Atômica", format="%.4f"),
        "nut_funcao": st.column_config.TextColumn("Função"),
        "nut_genero_id": None,  # Ocultar coluna original
        "nut_genero_desc": st.column_config.SelectboxColumn(
            "Gênero*",
            help="Selecione o gênero do nutriente",
            options=opcoes,
            required=True
        ) if opcoes else st.column_config.TextColumn("Gênero"),
        "nut_unidade_id": st.column_config.NumberColumn("Unidade ID", format="%d"),
        "nut_carencia": st.column_config.TextColumn("Sintomas de Carência"),
        "nut_excesso": st.column_config.TextColumn("Sintomas de Excesso")
    }
    
    df.reset_index(drop=True, inplace=True)
    
    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/nutrientes.png', width=48)
    with col2:
        st.subheader("Cadastro de Nutrientes")
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_tbl_nutrientes",
        hide_index=True
    )
    
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_nutrientes"):
            try:
                processed_df = edited_df.copy()
                
                # Converte descrições de volta para IDs
                if 'nut_genero_desc' in processed_df.columns:
                    processed_df['nut_genero_id'] = processed_df['nut_genero_desc'].map(desc_to_id)
                    processed_df = processed_df.drop(columns=['nut_genero_desc'])
                
                # Validação de campos obrigatórios
                required_cols = ["nut_codigo", "nut_nome", "nut_genero_id"]
                missing = False
                
                for idx, row in processed_df.iterrows():
                    for col in required_cols:
                        if col in row and pd.isna(row[col]):
                            field_name = col.replace("nut_", "")
                            st.warning(f"Linha {idx+1}: Campo '{field_name}' é obrigatório!")
                            missing = True
                
                if not missing:
                    if db_utils.save_data('tbl_nutrientes', processed_df):
                        st.success("Dados salvos com sucesso!")
                        st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")
    
    with col2:
        if st.button("🔄 Recarregar", key="btn_recarregar_tbl_nutrientes"):
            st.session_state.pop("editor_tbl_nutrientes", None)
            st.rerun()
    
    with col3:
        st.info(f"Tabela: tbl_nutrientes | Registros: {len(edited_df)}")

    
