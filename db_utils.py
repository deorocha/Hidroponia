# db_utils.py

# db_utils.py
import sqlite3
import os
import pandas as pd
from sqlite3 import Error

DB_PATH = './dados/hidroponia.db'

def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Criação de todas as tabelas
        tables = [
            """CREATE TABLE IF NOT EXISTS tbl_estufas (
                est_id INTEGER PRIMARY KEY AUTOINCREMENT,
                est_codigo TEXT NOT NULL,
                est_descricao TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_bancadas (
                bcd_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bcd_nome TEXT,
                bcd_descricao TEXT,
                bcd_qtd_furos INTEGER,
                bcd_id_tanque INTEGER,
                bcd_id_estufa INTEGER
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_tanques (
                tan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tan_nome TEXT,
                tan_capacidade REAL,
                tan_unidade TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_cultivares_generos (
                gen_id INTEGER PRIMARY KEY AUTOINCREMENT,
                gen_codigo TEXT,
                gen_nome TEXT,
                gen_descricao TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_cultivares (
                clt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                clt_genero_id INTEGER,
                clt_codigo TEXT,
                clt_nome TEXT,
                clt_nome_cientifico TEXT,
                clt_classificacao TEXT,
                clt_caracteristicas TEXT,
                FOREIGN KEY (clt_genero_id) REFERENCES tbl_cultivares_generos(gen_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_nutrientes_generos (
                nge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nge_descricao TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_nutrientes (
                nut_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nut_codigo TEXT,
                nut_tipo INTEGER,
                nut_nome TEXT,
                nut_simbolo TEXT,
                nut_massa_atomica REAL,
                nut_funcao TEXT,
                nut_genero_id INTEGER,
                nut_unidade_id INTEGER,
                nut_carencia TEXT,
                nut_excesso TEXT,
                FOREIGN KEY (nut_genero_id) REFERENCES tbl_nutrientes_generos(nge_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_solucoes (
                sol_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sol_nome TEXT,
                sol_descricao TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_faixas (
                fax_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fax_clt_id INTEGER,
                fax_nut_id INTEGER,
                fax_minimo NUMERIC (10,4),
                fax_maximo NUMERIC (10,4),
                FOREIGN KEY (fax_clt_id) REFERENCES tbl_cultivares(clt_id),
                FOREIGN KEY (fax_nut_id) REFERENCES tbl_nutrientes(nut_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_etapas_producao (
                etp_Id INTEGER PRIMARY KEY AUTOINCREMENT,
                etp_sistema_producao_id INTEGER,
                etp_nome TEXT,
                etp_descricao TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_fertilizantes (
                frt_Id INTEGER PRIMARY KEY AUTOINCREMENT,
                frt_Nome TEXT,
                frt_Formula TEXT,
                frt_Unidade_Id INTEGER,
                frt_Teor_Nominal REAL,
                frt_Teor_Efetivo REAL,
                frt_Nutriente_Id INTEGER,
                frt_Composicao TEXT,
                frt_Forma TEXT,
                frt_Solubilidade TEXT,
                frt_Obtencao TEXT,
                frt_Observacao TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS tbl_usuarios (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                verified INTEGER DEFAULT 0,
                confirmation_token TEXT,
                token_expiration TEXT
            )"""
        ]
        
        # Executar todos os comandos CREATE TABLE
        for table in tables:
            cursor.execute(table)
        
        conn.commit()
        return True
    except Error as e:
        print(f"Erro ao inicializar banco de dados: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_data(table_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        return df
    except Error as e:
        print(f"Erro ao obter dados da tabela {table_name}: {str(e)}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def save_data(table_name, df):
    try:
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        return True
    except Error as e:
        print(f"Erro ao salvar dados na tabela {table_name}: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def execute_query(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Erro na execução da query: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def fetch_one(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    except Error as e:
        print(f"Erro ao buscar dados: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()
