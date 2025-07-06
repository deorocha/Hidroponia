# cadastro_tanques.py

import streamlit as st
import pandas as pd
import sqlite3
import db_utils

def show():
    # Verificar/criar tabela se não existir
    try:
        conn = sqlite3.connect('./dados/hidroponia.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tbl_tanques (
                tan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tan_nome TEXT NOT NULL UNIQUE,
                tan_capacidade REAL,
                tan_unidade TEXT
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
        st.image('./imagens/tanques.png', width=48)
    with col2:
        st.subheader("Cadastro de Tanques")
    
    # Inicializar session_state para o DataFrame dos tanques
    if 'df_tanques' not in st.session_state:
        try:
            df = db_utils.get_data('tbl_tanques')
            if df.empty:
                df = pd.DataFrame(columns=["tan_id", "tan_nome", "tan_capacidade", "tan_unidade"])
            else:
                df['tan_id'] = df['tan_id'].astype('Int64')
            st.session_state.df_tanques = df
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            st.session_state.df_tanques = pd.DataFrame(
                columns=["tan_id", "tan_nome", "tan_capacidade", "tan_unidade"]
            )
    
    column_config = {
        "tan_id": st.column_config.NumberColumn("ID", disabled=True),
        "tan_nome": st.column_config.TextColumn("Nome*", required=True),
        "tan_capacidade": st.column_config.NumberColumn("Capacidade", format="%.2f"),
        "tan_unidade": st.column_config.TextColumn("Unidade")
    }
    
    # Usar o DataFrame do session_state
    edited_df = st.data_editor(
        st.session_state.df_tanques,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_tbl_tanques"
    )
    
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        if st.button("💾 Salvar", key="btn_salvar_tbl_tanques"):
            try:
                # Validação reforçada
                missing = False
                duplicates = False
                
                # 1. Verificar campos obrigatórios
                for idx, row in edited_df.iterrows():
                    if pd.isna(row.get('tan_nome')) or str(row['tan_nome']).strip() == '':
                        st.warning(f"Linha {idx+1}: Campo 'Nome' é obrigatório!")
                        missing = True
                
                # 2. Verificar duplicatas no DataFrame
                nome_counts = edited_df['tan_nome'].value_counts()
                if any(nome_counts > 1):
                    dup_names = nome_counts[nome_counts > 1].index.tolist()
                    st.warning(f"Nomes duplicados no formulário: {', '.join(dup_names)}")
                    duplicates = True
                
                # 3. Verificar duplicatas no banco de dados
                if not duplicates and not missing:
                    try:
                        conn = sqlite3.connect('./dados/hidroponia.db')
                        cursor = conn.cursor()
                        cursor.execute("SELECT tan_nome, tan_id FROM tbl_tanques")
                        existing_records = {row[0]: row[1] for row in cursor.fetchall()}
                        
                        new_duplicates = []
                        for idx, row in edited_df.iterrows():
                            current_name = str(row['tan_nome']).strip()
                            
                            # Verificar se é um novo registro ou nome alterado
                            if pd.isna(row['tan_id']):  # Novo registro
                                if current_name in existing_records:
                                    new_duplicates.append(current_name)
                            else:  # Registro existente
                                # Buscar nome original no session_state
                                original_name = str(st.session_state.df_tanques.loc[idx, 'tan_nome']).strip()
                                if current_name != original_name:
                                    # Verificar se o novo nome já existe
                                    if current_name in existing_records:
                                        # Verificar se não é o mesmo registro
                                        if existing_records[current_name] != int(row['tan_id']):
                                            new_duplicates.append(current_name)
                        
                        if new_duplicates:
                            st.warning(
                                f"Nomes já existentes no banco: {', '.join(set(new_duplicates))}"
                            )
                            duplicates = True
                    except Exception as e:
                        st.error(f"Erro ao verificar duplicatas: {str(e)}")
                        duplicates = True
                    finally:
                        if conn:
                            conn.close()
                
                if not missing and not duplicates:
                    conn = sqlite3.connect('./dados/hidroponia.db')
                    try:
                        # Criar uma cópia para evitar SettingWithCopyWarning
                        updated_df = edited_df.copy()
                        
                        # Salvar usando UPSERT
                        for index, row in updated_df.iterrows():
                            # Converter para string e remover espaços
                            nome = str(row['tan_nome']).strip() if not pd.isna(row['tan_nome']) else None
                            
                            # Tratar capacidade (converter para float se possível)
                            capacidade = row['tan_capacidade']
                            if not pd.isna(capacidade):
                                try:
                                    capacidade = float(capacidade)
                                except (ValueError, TypeError):
                                    capacidade = None
                            
                            # Tratar unidade
                            unidade = str(row['tan_unidade']).strip() if not pd.isna(row['tan_unidade']) else None
                            
                            if pd.notna(row['tan_id']):
                                # Atualizar registro existente
                                cursor = conn.cursor()
                                cursor.execute(
                                    "UPDATE tbl_tanques SET "
                                    "tan_nome = ?, "
                                    "tan_capacidade = ?, "
                                    "tan_unidade = ? "
                                    "WHERE tan_id = ?",
                                    (nome, capacidade, unidade, int(row['tan_id']))
                                )
                            else:
                                # Inserir novo registro e capturar ID
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO tbl_tanques "
                                    "(tan_nome, tan_capacidade, tan_unidade) "
                                    "VALUES (?, ?, ?)",
                                    (nome, capacidade, unidade)
                                )
                                # Atualizar ID imediatamente
                                updated_df.at[index, 'tan_id'] = cursor.lastrowid
                        
                        conn.commit()
                        
                        # Atualizar session_state com IDs corrigidos
                        st.session_state.df_tanques = updated_df
                        st.success("Dados salvos com sucesso!")
                        
                        # Forçar rerun para atualizar o editor com os novos IDs
                        st.rerun()
                        
                    except sqlite3.IntegrityError as e:
                        st.error(f"Erro de duplicação: {str(e)}")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {str(e)}")
                    finally:
                        conn.close()
            except Exception as e:
                st.error(f"Erro ao validar: {str(e)}")
    
    with col2:
        if st.button("🔄 Recarregar", key="btn_recarregar_tbl_tanques"):
            try:
                # Recarregar dados do banco
                df = db_utils.get_data('tbl_tanques')
                if df.empty:
                    df = pd.DataFrame(columns=["tan_id", "tan_nome", "tan_capacidade", "tan_unidade"])
                else:
                    df['tan_id'] = df['tan_id'].astype('Int64')
                st.session_state.df_tanques = df
                st.success("Dados recarregados do banco!")
            except Exception as e:
                st.error(f"Erro ao recarregar: {str(e)}")
    
    with col3:
        st.info(f"Tabela: tbl_tanques | Registros: {len(edited_df)}")

# Chamada da função principal
if __name__ == "__main__":
    show()
