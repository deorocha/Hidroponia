# cadastro_bancadas.py

import streamlit as st
import pandas as pd
import db_utils
import sqlite3
import numpy as np

def show():
    # Verificar/criar tabela se não existir
    try:
        conn = sqlite3.connect('./dados/hidroponia.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tbl_bancadas (
                bcd_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bcd_nome TEXT NOT NULL UNIQUE,
                bcd_descricao TEXT,
                bcd_qtd_furos INTEGER,
                bcd_tanque_id INTEGER,
                bcd_estufa_id INTEGER,
                FOREIGN KEY (bcd_tanque_id) REFERENCES tbl_tanques(tan_id),
                FOREIGN KEY (bcd_estufa_id) REFERENCES tbl_estufas(est_id)
            )
        ''')
        conn.commit()
    except Exception as e:
        st.error(f"Erro ao verificar/criar tabela: {str(e)}")
    finally:
        if conn:
            conn.close()

    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/bancadas.png', width=48)
    with col2:
        st.subheader("Cadastro de Bancadas")
    
    # Obter dados para os dropdowns
    try:
        tanques = db_utils.get_data('tbl_tanques')
        tanque_options = {row['tan_id']: row['tan_descricao'] for _, row in tanques.iterrows()} if not tanques.empty else {}
        tanque_name_to_id = {name: id for id, name in tanque_options.items()}
    except Exception as e:
        st.error(f"Erro ao carregar tanques: {str(e)}")
        tanque_options = {}
        tanque_name_to_id = {}
    
    try:
        estufas = db_utils.get_data('tbl_estufas')
        estufa_options = {row['est_id']: row['est_codigo'] for _, row in estufas.iterrows()} if not estufas.empty else {}
        estufa_name_to_id = {name: id for id, name in estufa_options.items()}
    except Exception as e:
        st.error(f"Erro ao carregar estufas: {str(e)}")
        estufa_options = {}
        estufa_name_to_id = {}
    
    # Obter dados das bancadas
    try:
        df = db_utils.get_data('tbl_bancadas')
        if df.empty:
            df = pd.DataFrame(columns=["bcd_id", "bcd_nome", "bcd_descricao", "bcd_qtd_furos", "bcd_tanque_id", "bcd_estufa_id"])
        else:
            # Garantir que IDs são números inteiros
            df['bcd_id'] = df['bcd_id'].astype('Int64')
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        df = pd.DataFrame(columns=["bcd_id", "bcd_nome", "bcd_descricao", "bcd_qtd_furos", "bcd_tanque_id", "bcd_estufa_id"])
    
    # Adicionar colunas temporárias para exibição
    df['tanque_nome'] = df['bcd_tanque_id'].map(lambda x: tanque_options.get(x, "Não selecionado"))
    df['estufa_nome'] = df['bcd_estufa_id'].map(lambda x: estufa_options.get(x, "Não selecionado"))
    
    # Garantir tipos de dados corretos
    for col in ["bcd_id", "bcd_tanque_id", "bcd_estufa_id"]:
        if col in df.columns and df[col].dtype != 'Int64':
            df[col] = df[col].astype('Int64')
    
    column_config = {
        "bcd_id": st.column_config.NumberColumn("ID", disabled=True),
        "bcd_nome": st.column_config.TextColumn("Nome*", required=True),
        "bcd_descricao": st.column_config.TextColumn("Descrição"),
        "bcd_qtd_furos": st.column_config.NumberColumn("Qtd.furos"),
        "tanque_nome": st.column_config.SelectboxColumn(
            "Tanque",
            options=["Não selecionado"] + list(tanque_options.values()),
            help="Selecione o tanque associado"
        ),
        "estufa_nome": st.column_config.SelectboxColumn(
            "Estufa",
            options=["Não selecionado"] + list(estufa_options.values()),
            help="Selecione a estufa associada"
        )
    }
    
    # Garantir que temos as colunas esperadas
    for col in column_config.keys():
        if col not in df.columns:
            df[col] = None
    
    # Converter IDs para Int64 para evitar problemas com NaN
    for col in ["bcd_tanque_id", "bcd_estufa_id"]:
        if col in df.columns:
            df[col] = df[col].astype('Int64')
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_tbl_bancadas",
        column_order=["bcd_id", "bcd_nome", "bcd_descricao", "bcd_qtd_furos", "tanque_nome", "estufa_nome"]
    )
    
    # Atualizar IDs com base nas seleções
    edited_df['bcd_tanque_id'] = edited_df['tanque_nome'].map(tanque_name_to_id)
    edited_df['bcd_estufa_id'] = edited_df['estufa_nome'].map(estufa_name_to_id)
    
    # Tratar casos onde nenhum tanque/estufa foi selecionado
    edited_df['bcd_tanque_id'] = edited_df['bcd_tanque_id'].where(
        edited_df['tanque_nome'] != "Não selecionado", 
        pd.NA
    )
    edited_df['bcd_estufa_id'] = edited_df['bcd_estufa_id'].where(
        edited_df['estufa_nome'] != "Não selecionado", 
        pd.NA
    )
    
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_bancadas"):
            try:
                # Validação
                required_cols = ["bcd_nome"]
                
                missing = False
                for idx, row in edited_df.iterrows():
                    for col in required_cols:
                        if col in row and pd.isna(row[col]):
                            st.warning(f"Linha {idx+1}: Campo '{col}' é obrigatório!")
                            missing = True
                
                # Verificar nomes duplicados
                duplicates = edited_df['bcd_nome'].duplicated()
                if duplicates.any():
                    dup_names = edited_df[duplicates]['bcd_nome'].unique()
                    st.warning(f"Nomes duplicados encontrados: {', '.join(dup_names)}")
                    missing = True
                
                if not missing:
                    try:
                        # Remover colunas temporárias
                        save_df = edited_df[["bcd_id", "bcd_nome", "bcd_descricao", "bcd_qtd_furos", "bcd_tanque_id", "bcd_estufa_id"]].copy()
                        
                        # Salvar usando UPSERT para manter AUTOINCREMENT
                        conn = sqlite3.connect('./dados/hidroponia.db')
                        cursor = conn.cursor()
                        
                        for _, row in save_df.iterrows():
                            data = {
                                'bcd_id': row['bcd_id'],
                                'bcd_nome': row['bcd_nome'],
                                'bcd_descricao': row['bcd_descricao'] if not pd.isna(row['bcd_descricao']) else None,
                                'bcd_qtd_furos': row['bcd_qtd_furos'] if not pd.isna(row['bcd_qtd_furos']) else None,
                                'bcd_tanque_id': row['bcd_tanque_id'] if not pd.isna(row['bcd_tanque_id']) else None,
                                'bcd_estufa_id': row['bcd_estufa_id'] if not pd.isna(row['bcd_estufa_id']) else None
                            }
                            
                            if pd.notna(data['bcd_id']):
                                # UPDATE para registro existente
                                cursor.execute('''
                                    UPDATE tbl_bancadas 
                                    SET bcd_nome = :bcd_nome, 
                                        bcd_descricao = :bcd_descricao,
                                        bcd_qtd_furos = :bcd_qtd_furos,
                                        bcd_tanque_id = :bcd_tanque_id,
                                        bcd_estufa_id = :bcd_estufa_id
                                    WHERE bcd_id = :bcd_id
                                ''', data)
                            else:
                                # INSERT para novo registro
                                cursor.execute('''
                                    INSERT INTO tbl_bancadas 
                                    (bcd_nome, bcd_descricao, bcd_qtd_furos, bcd_tanque_id, bcd_estufa_id)
                                    VALUES (:bcd_nome, :bcd_descricao, :bcd_qtd_furos, :bcd_tanque_id, :bcd_estufa_id)
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
        if st.button("🔄 Recarregar", key="btn_recarregar_tbl_bancadas"):
            st.session_state.pop("editor_tbl_bancadas", None)
            st.rerun()
    
    with col3:
        st.info(f"Tabela: tbl_bancadas | Registros: {len(edited_df)}")
