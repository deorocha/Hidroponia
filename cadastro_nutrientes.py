# cadastro_nutrientes.py

import streamlit as st
import pandas as pd
import db_utils
import sqlite3
import numpy as np

def show():
    # Verificar/criar tabelas se não existirem
    try:
        conn = sqlite3.connect('./dados/hidroponia.db')
        # Criar tbl_nutrientes_generos se não existir
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tbl_nutrientes_generos (
                nge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nge_descricao TEXT
            )
        ''')
        # Criar tbl_nutrientes se não existir
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tbl_nutrientes (
                nut_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nut_codigo TEXT,
                nut_tipo INTEGER,
                nut_nome TEXT NOT NULL,
                nut_simbolo TEXT,
                nut_massa_atomica REAL,
                nut_funcao TEXT,
                nut_genero_id INTEGER,
                nut_unidade_id INTEGER,
                nut_carencia TEXT,
                nut_excesso TEXT,
                FOREIGN KEY (nut_genero_id) REFERENCES tbl_nutrientes_generos(nge_id)
            )
        ''')
        conn.commit()
    except Exception as e:
        st.error(f"Erro ao verificar/criar tabelas: {str(e)}")
    finally:
        if conn:
            conn.close()

    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/nutrientes.png', width=48)
    with col2:
        st.subheader("Cadastro de Nutrientes")
    
    # Obter dados para os dropdowns (gêneros de nutrientes)
    try:
        generos_df = db_utils.get_data('tbl_nutrientes_generos')
        genero_options = {}
        genero_name_to_id = {}
        if not generos_df.empty:
            genero_options = {row['nge_id']: row['nge_descricao'] for _, row in generos_df.iterrows()}
            genero_name_to_id = {desc: id for id, desc in genero_options.items()}
    except Exception as e:
        st.error(f"Erro ao carregar gêneros de nutrientes: {str(e)}")
        genero_options = {}
        genero_name_to_id = {}
    
    # Obter dados dos nutrientes
    try:
        df = db_utils.get_data('tbl_nutrientes')
        if df.empty:
            df = pd.DataFrame(columns=[
                "nut_id", "nut_codigo", "nut_tipo", "nut_nome", "nut_simbolo",
                "nut_massa_atomica", "nut_funcao", "nut_genero_id", 
                "nut_unidade_id", "nut_carencia", "nut_excesso"
            ])
        else:
            # Garantir que IDs são números inteiros
            df['nut_id'] = df['nut_id'].astype('Int64')
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        df = pd.DataFrame(columns=[
            "nut_id", "nut_codigo", "nut_tipo", "nut_nome", "nut_simbolo",
            "nut_massa_atomica", "nut_funcao", "nut_genero_id", 
            "nut_unidade_id", "nut_carencia", "nut_excesso"
        ])
    
    # Adicionar coluna temporária para exibição do gênero
    df['genero_desc'] = df['nut_genero_id'].map(
        lambda x: genero_options.get(x, "Não selecionado") if pd.notna(x) else "Não selecionado"
    )
    
    # Garantir tipos de dados corretos
    for col in ["nut_id", "nut_genero_id", "nut_unidade_id"]:
        if col in df.columns and df[col].dtype != 'Int64':
            df[col] = df[col].astype('Int64')
    
    column_config = {
        "nut_id": st.column_config.NumberColumn("ID", disabled=True),
        "nut_codigo": st.column_config.TextColumn("Código*", required=True),
        "nut_nome": st.column_config.TextColumn("Nome*", required=True),
        "nut_simbolo": st.column_config.TextColumn("Símbolo"),
        "nut_massa_atomica": st.column_config.NumberColumn("Massa Atômica", format="%.4f"),
        "nut_funcao": st.column_config.TextColumn("Função"),
        "nut_genero_id": None,  # Ocultar coluna original
        "genero_desc": st.column_config.SelectboxColumn(
            "Gênero",
            options=["Não selecionado"] + list(genero_options.values()),
            help="Selecione o gênero do nutriente"
        ),
        "nut_unidade_id": st.column_config.NumberColumn("Unidade ID", format="%d"),
        "nut_carencia": st.column_config.TextColumn("Sintomas de Carência"),
        "nut_excesso": st.column_config.TextColumn("Sintomas de Excesso")
    }
    
    # Garantir que temos as colunas esperadas
    for col in column_config.keys():
        if col not in df.columns:
            df[col] = None
    
    # Converter IDs para Int64 para evitar problemas com NaN
    for col in ["nut_genero_id"]:
        if col in df.columns:
            df[col] = df[col].astype('Int64')
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_tbl_nutrientes",
        column_order=["nut_id", "nut_codigo", "nut_nome", "nut_simbolo", 
                      "nut_massa_atomica", "nut_funcao", "genero_desc",
                      "nut_unidade_id", "nut_carencia", "nut_excesso"]
    )
    
    # Atualizar IDs com base nas seleções
    edited_df['nut_genero_id'] = edited_df['genero_desc'].map(genero_name_to_id)
    
    # Tratar casos onde nenhum gênero foi selecionado
    edited_df['nut_genero_id'] = edited_df['nut_genero_id'].where(
        edited_df['genero_desc'] != "Não selecionado", 
        pd.NA
    )
    
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_nutrientes"):
            try:
                # Validação
                required_cols = ["nut_codigo", "nut_nome"]
                
                missing = False
                for idx, row in edited_df.iterrows():
                    for col in required_cols:
                        if col in row and pd.isna(row[col]):
                            st.warning(f"Linha {idx+1}: Campo '{col}' é obrigatório!")
                            missing = True
                
                # Verificar códigos duplicados
                duplicates = edited_df['nut_codigo'].duplicated()
                if duplicates.any():
                    dup_codes = edited_df[duplicates]['nut_codigo'].unique()
                    st.warning(f"Códigos duplicados encontrados: {', '.join(dup_codes)}")
                    missing = True
                
                if not missing:
                    try:
                        # Remover colunas temporárias
                        save_df = edited_df[[
                            "nut_id", "nut_codigo", "nut_tipo", "nut_nome", "nut_simbolo",
                            "nut_massa_atomica", "nut_funcao", "nut_genero_id", 
                            "nut_unidade_id", "nut_carencia", "nut_excesso"
                        ]].copy()
                        
                        # Salvar usando UPSERT para manter AUTOINCREMENT
                        conn = sqlite3.connect('./dados/hidroponia.db')
                        cursor = conn.cursor()
                        
                        for _, row in save_df.iterrows():
                            data = {
                                'nut_id': row['nut_id'],
                                'nut_codigo': row['nut_codigo'],
                                'nut_tipo': row['nut_tipo'] if not pd.isna(row['nut_tipo']) else None,
                                'nut_nome': row['nut_nome'],
                                'nut_simbolo': row['nut_simbolo'] if not pd.isna(row['nut_simbolo']) else None,
                                'nut_massa_atomica': row['nut_massa_atomica'] if not pd.isna(row['nut_massa_atomica']) else None,
                                'nut_funcao': row['nut_funcao'] if not pd.isna(row['nut_funcao']) else None,
                                'nut_genero_id': row['nut_genero_id'] if not pd.isna(row['nut_genero_id']) else None,
                                'nut_unidade_id': row['nut_unidade_id'] if not pd.isna(row['nut_unidade_id']) else None,
                                'nut_carencia': row['nut_carencia'] if not pd.isna(row['nut_carencia']) else None,
                                'nut_excesso': row['nut_excesso'] if not pd.isna(row['nut_excesso']) else None
                            }
                            
                            if pd.notna(data['nut_id']):
                                # UPDATE para registro existente
                                cursor.execute('''
                                    UPDATE tbl_nutrientes 
                                    SET nut_codigo = :nut_codigo,
                                        nut_tipo = :nut_tipo,
                                        nut_nome = :nut_nome,
                                        nut_simbolo = :nut_simbolo,
                                        nut_massa_atomica = :nut_massa_atomica,
                                        nut_funcao = :nut_funcao,
                                        nut_genero_id = :nut_genero_id,
                                        nut_unidade_id = :nut_unidade_id,
                                        nut_carencia = :nut_carencia,
                                        nut_excesso = :nut_excesso
                                    WHERE nut_id = :nut_id
                                ''', data)
                            else:
                                # INSERT para novo registro
                                cursor.execute('''
                                    INSERT INTO tbl_nutrientes 
                                    (nut_codigo, nut_tipo, nut_nome, nut_simbolo, 
                                     nut_massa_atomica, nut_funcao, nut_genero_id, 
                                     nut_unidade_id, nut_carencia, nut_excesso) 
                                    VALUES 
                                    (:nut_codigo, :nut_tipo, :nut_nome, :nut_simbolo, 
                                     :nut_massa_atomica, :nut_funcao, :nut_genero_id, 
                                     :nut_unidade_id, :nut_carencia, :nut_excesso)
                                ''', data)
                        
                        conn.commit()
                        st.success("Dados salvos com sucesso!")
                        st.rerun()
                    except sqlite3.IntegrityError as e:
                        st.error(f"Erro de integridade: {str(e)}")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {str(e)}")
                    finally:
                        if conn:
                            conn.close()
            except Exception as e:
                st.error(f"Erro ao validar: {str(e)}")
    
    with col2:
        if st.button("🔄 Recarregar", key="btn_recarregar_tbl_nutrientes"):
            st.session_state.pop("editor_tbl_nutrientes", None)
            st.rerun()
    
    with col3:
        st.info(f"Tabela: tbl_nutrientes | Registros: {len(edited_df)}")
