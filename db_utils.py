# db_utils.py

import sqlite3
import pandas as pd
import streamlit as st

def init_db():
    """Garante que o banco de dados e tabelas existam"""
    pass

def get_data(table_name):
    """Obtém dados de uma tabela como DataFrame"""
    try:
        conn = sqlite3.connect('hidroponia.db')
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        
        id_column = get_id_column(table_name)
        if id_column and id_column in df.columns:
            df[id_column] = df[id_column].astype('Int64')
            
        df.reset_index(drop=True, inplace=True)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def get_generos_nutrientes():
    """Carrega os gêneros de nutrientes para o combobox"""
    try:
        conn = sqlite3.connect('hidroponia.db')
        query = "SELECT nge_id, nge_descricao FROM tbl_nutrientes_generos"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Retorna como lista de tuplas (id, descrição)
        return [(row['nge_id'], row['nge_descricao']) for _, row in df.iterrows()]
    except Exception as e:
        st.error(f"Erro ao carregar gêneros: {str(e)}")
        return []

def get_id_column(table_name):
    """Retorna o nome da coluna ID para cada tabela"""
    id_columns = {
        'tbl_bancadas': 'bcd_id',
        'tbl_cultivares': 'clt_id',
        'tbl_nutrientes': 'nut_id',
        'tbl_solucoes': 'sol_id',
        'tbl_tanques': 'tan_id'
    }
    return id_columns.get(table_name, 'id')

def save_data(table_name, df):
    """Salva os dados de volta no banco de dados"""
    try:
        conn = sqlite3.connect('hidroponia.db')
        c = conn.cursor()
        
        df = df.dropna(how='all')
        id_column = get_id_column(table_name)
        
        if id_column in df.columns:
            existing = df[df[id_column].notna()]
            new = df[df[id_column].isna()]
        else:
            existing = pd.DataFrame()
            new = df
        
        for _, row in existing.iterrows():
            id_val = int(row[id_column])
            
            if table_name == 'tbl_bancadas':
                c.execute('''UPDATE tbl_bancadas 
                            SET bcd_nome=?, bcd_descricao=?, bcd_id_tanque=? 
                            WHERE bcd_id=?''', 
                          (row['bcd_nome'], row.get('bcd_descricao', ''), 
                           row.get('bcd_id_tanque', None), id_val))
            
            elif table_name == 'tbl_cultivares':
                c.execute('''UPDATE tbl_cultivares 
                            SET clt_genero_id=?, clt_codigo=?, clt_nome=?, 
                                clt_nome_cientifico=?, clt_classificacao=?, clt_caracteristicas=? 
                            WHERE clt_id=?''', 
                          (row.get('clt_genero_id', None), row.get('clt_codigo', ''), 
                           row.get('clt_nome', ''), row.get('clt_nome_cientifico', ''), 
                           row.get('clt_classificacao', ''), row.get('clt_caracteristicas', ''), id_val))
            
            elif table_name == 'tbl_nutrientes':
                massa_atomica = row.get('nut_massa_atomica', None)
                if massa_atomica is not None and pd.isna(massa_atomica):
                    massa_atomica = None
                
                c.execute('''UPDATE tbl_nutrientes 
                            SET nut_codigo=?, nut_nome=?, nut_simbolo=?, 
                                nut_massa_atomica=?, nut_funcao=?, nut_genero_id=?, 
                                nut_unidade_id=?, nut_carencia=?, nut_excesso=? 
                            WHERE nut_id=?''', 
                          (row.get('nut_codigo', ''), row.get('nut_nome', ''), 
                           row.get('nut_simbolo', ''), massa_atomica, 
                           row.get('nut_funcao', ''), row.get('nut_genero_id', None), 
                           row.get('nut_unidade_id', None), row.get('nut_carencia', ''), 
                           row.get('nut_excesso', ''), id_val))
            
            elif table_name == 'tbl_solucoes':
                c.execute('''UPDATE tbl_solucoes 
                            SET sol_nome=?, sol_descricao=? 
                            WHERE sol_id=?''', 
                          (row['sol_nome'], row.get('sol_descricao', ''), id_val))
            
            elif table_name == 'tbl_tanques':
                c.execute('''UPDATE tbl_tanques 
                            SET tan_nome=?, tan_capacidade=?, tan_unidade=? 
                            WHERE tan_id=?''', 
                          (row['tan_nome'], row.get('tan_capacidade', None), 
                           row.get('tan_unidade', ''), id_val))
        
        for _, row in new.iterrows():
            if table_name == 'tbl_bancadas':
                c.execute('''INSERT INTO tbl_bancadas (bcd_nome, bcd_descricao, bcd_id_tanque) 
                            VALUES (?, ?, ?)''', 
                          (row['bcd_nome'], row.get('bcd_descricao', ''), 
                           row.get('bcd_id_tanque', None)))
            
            elif table_name == 'tbl_cultivares':
                c.execute('''INSERT INTO tbl_cultivares (clt_genero_id, clt_codigo, clt_nome, 
                                                        clt_nome_cientifico, clt_classificacao, clt_caracteristicas) 
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                          (row.get('clt_genero_id', None), row.get('clt_codigo', ''), 
                           row.get('clt_nome', ''), row.get('clt_nome_cientifico', ''), 
                           row.get('clt_classificacao', ''), row.get('clt_caracteristicas', '')))
            
            elif table_name == 'tbl_nutrientes':
                massa_atomica = row.get('nut_massa_atomica', None)
                if massa_atomica is not None and pd.isna(massa_atomica):
                    massa_atomica = None
                
                c.execute('''INSERT INTO tbl_nutrientes (nut_codigo, nut_nome, nut_simbolo, 
                                                        nut_massa_atomica, nut_funcao, nut_genero_id, 
                                                        nut_unidade_id, nut_carencia, nut_excesso) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (row.get('nut_codigo', ''), row.get('nut_nome', ''), 
                           row.get('nut_simbolo', ''), massa_atomica, 
                           row.get('nut_funcao', ''), row.get('nut_genero_id', None), 
                           row.get('nut_unidade_id', None), row.get('nut_carencia', ''), 
                           row.get('nut_excesso', '')))
            
            elif table_name == 'tbl_solucoes':
                c.execute('''INSERT INTO tbl_solucoes (sol_nome, sol_descricao) 
                            VALUES (?, ?)''', 
                          (row['sol_nome'], row.get('sol_descricao', '')))
            
            elif table_name == 'tbl_tanques':
                c.execute('''INSERT INTO tbl_tanques (tan_nome, tan_capacidade, tan_unidade) 
                            VALUES (?, ?, ?)''', 
                          (row['tan_nome'], row.get('tan_capacidade', None), 
                           row.get('tan_unidade', '')))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {str(e)}")
        return False
