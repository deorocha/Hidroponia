# cadastro_cultivares.py

import streamlit as st
import pandas as pd
import numpy as np
import db_utils

def show():
    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/cultivares.png', width=48)
    with col2:
        st.subheader("Cadastro de Cultivares")
    
    # Carregar dados dos gêneros para o selectbox
    try:
        generos_df = db_utils.get_data('tbl_cultivares_generos')
        # Criar dicionário de opções: {gen_id: gen_nome}
        generos_options = generos_df.set_index('gen_id')['gen_nome'].to_dict()
        # Criar mapeamento reverso de nome para ID (com tratamento de valores nulos)
        nome_to_id = {str(v).strip(): k for k, v in generos_options.items() if v is not None}
    except Exception as e:
        st.error(f"Erro ao carregar gêneros: {str(e)}")
        generos_options = {}
        nome_to_id = {}
    
    try:
        df = db_utils.get_data('tbl_cultivares')
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        df = pd.DataFrame()
    
    # Adicionar coluna de seleção se não existir
    if 'clt_selecionado' not in df.columns:
        df['clt_selecionado'] = 0
    
    if df.empty:
        df = pd.DataFrame(columns=[
            "clt_id", "clt_genero_id", "clt_codigo", "clt_nome", 
            "clt_nome_cientifico", "clt_classificacao", "clt_caracteristicas",
            "clt_selecionado"
        ])
    
    # Criar coluna temporária para exibição do nome do gênero
    if not df.empty and generos_options:
        # Adicionar coluna temporária para exibição
        df['Gênero'] = df['clt_genero_id'].map(generos_options)
        # Preencher valores ausentes e None com string vazia
        df['Gênero'] = df['Gênero'].fillna('')
    else:
        df['Gênero'] = ""
    
    column_config = {
        "clt_id": st.column_config.NumberColumn("ID", disabled=True),
        "clt_selecionado": st.column_config.CheckboxColumn("Selecionado"),
        "clt_genero_id": st.column_config.Column(disabled=True),
        "clt_codigo": st.column_config.TextColumn("Código"),
        "clt_nome": st.column_config.TextColumn("Nome"),
        "clt_nome_cientifico": st.column_config.TextColumn("Nome Científico"),
        "clt_classificacao": st.column_config.TextColumn("Classificação"),
        "clt_caracteristicas": st.column_config.TextColumn("Características"),
        "Gênero": st.column_config.SelectboxColumn(
            "Gênero",
            options=list(generos_options.values()),
            required=True
        )
    }
    
    # Definir ordem das colunas
    column_order = [
        "clt_id", "clt_selecionado", "Gênero", "clt_codigo", "clt_nome", 
        "clt_nome_cientifico", "clt_classificacao", "clt_caracteristicas"
    ]
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_tbl_cultivares",
        hide_index=True,
        column_order=column_order
    )
    
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_cultivares"):
            try:
                # Tratar valores None na coluna Gênero
                edited_df['Gênero'] = edited_df['Gênero'].fillna('')
                
                # Verificar se há valores vazios na coluna Gênero
                if edited_df['Gênero'].eq('').any():
                    # Identificar as linhas com problemas
                    empty_gen_rows = edited_df[edited_df['Gênero'] == ''].index.tolist()
                    st.error(f"Erro: Gênero não selecionado nas linhas: {empty_gen_rows}")
                    return
                
                # Remover espaços extras dos nomes
                edited_df['Gênero'] = edited_df['Gênero'].str.strip()
                
                # Converter nome do gênero de volta para ID
                edited_df['clt_genero_id'] = edited_df['Gênero'].map(nome_to_id)
                
                # Tratar valores não mapeados (None resultantes do map)
                edited_df['clt_genero_id'] = edited_df['clt_genero_id'].replace({np.nan: None})
                
                # Verificar se há valores não mapeados
                if edited_df['clt_genero_id'].isna().any():
                    # Identificar os valores problemáticos
                    invalid_rows = edited_df[edited_df['clt_genero_id'].isna()]
                    invalid_gen = invalid_rows['Gênero'].unique()
                    
                    # Formatar mensagem de erro detalhada
                    error_msg = "Erro: Gêneros inválidos selecionados:\n"
                    for i, row in invalid_rows.iterrows():
                        error_msg += f"Linha {i}: '{row['Gênero']}'\n"
                    
                    st.error(error_msg)
                    return
                
                # Converter checkbox para 0/1 antes de salvar
                edited_df['clt_selecionado'] = edited_df['clt_selecionado'].astype(int)
                
                # Remover coluna temporária antes de salvar
                edited_df = edited_df.drop(columns=['Gênero'])
                
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
