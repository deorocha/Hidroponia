# cadastros.py

import streamlit as st
from streamlit_scroll_navigation import scroll_navbar
import unicodedata
import sqlite3

col1, col2 = st.columns([10,200])
with col1:
    st.image('./imagens/cadastros.png', width=48)
with col2:
    st.subheader("Cadastros")

st.caption("Cadastre as principais tabelas do Sistema")

pages = {
    "Cadastros": [
        st.Page("cadastro_bancadas.py", title="🎍 Bancadas"),
        st.Page("cadastro_cultivares.py", title="🥬 Cultivares"),
        st.Page("cadastro_nutrientes.py", title="🧬 Nutrientes"),
        st.Page("cadastro_solucoes.py", title="🧪 Soluções"),
        st.Page("cadastro_tanques.py", title="🚰 Tanques"),
    ],
    "Configurações": [
        st.Page("configuracoes.py", title="⚙️ Configurações"),
        st.Page("sobre.py", title="ℹ️ Sobre nós..."),
        st.Page("email.py", title="📩 Fale conosco."),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()

def nome_imagem(texto):
    texto_under = texto.replace(" ", "_")
    texto_limpo = "".join(c for c in unicodedata.normalize('NFKD', texto_under) if not unicodedata.combining(c))
    return ("./imagens/cultivares/" + texto_limpo + ".png").lower()

def load_cultivares_data():
    try:
        conn = sqlite3.connect('hidroponia.db')
        cursor = conn.cursor()
        
        # Carregar dados da tabela tbl_cultivares
        cursor.execute("SELECT clt_id, clt_descricao, clt_nome_cientifico, clt_classificacao, clt_caracteristicas FROM tbl_cultivares")
        cultivares = cursor.fetchall() or [] # Garante lista vazia se None
        
        # Inicializar listas (garante que existirão mesmo sem dados)
        col_id = []
        col_descricao = []
        col_nome_cientifico = []
        col_classificacao = []
        col_caracteristicas = []
        col_nome_imagem = []

        if cultivares:
            for clt_id, clt_descricao, clt_nome_cientifico, clt_classificacao, clt_caracteristicas in cultivares:
                col_id.append(clt_id)
                col_descricao.append(clt_descricao)
                col_nome_cientifico.append(clt_nome_cientifico)
                col_classificacao.append(clt_classificacao)
                col_caracteristicas.append(clt_caracteristicas)
                col_nome_imagem.append(nome_imagem(clt_descricao))

        conn.close()
        
        return {
            'id': col_id,
            'descricao': col_descricao,
            'nome_cientifico': col_nome_cientifico,
            'classificacao': col_classificacao,
            'caracteristicas': col_caracteristicas,
            'nome_imagem': col_nome_imagem
        }
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        # Retorna estruturas vazias em caso de erro
        return {
            'id': [],
            'descricao': [],
            'nome_cientifico': [],
            'classificacao': [],
            'caracteristicas': [],
            'nome_imagem': []
        }

# ------------------------------
# Carregar dados com cache
@st.cache_data
def load_cultivares():
    return load_cultivares_data()

def main():
    st.markdown(f"""
        <style>
        html, body, [class*="css"] {{
            font-size: 15px;
        }}

        .block-container {{
            padding-top: 3rem;
            padding-bottom: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}

        .st-emotion-cache-1f3w014 {{
            height: 2rem;
            width : 2rem;
            background-color: GREEN;
        }}
        </style>
    """, unsafe_allow_html=True)

    # ------------------------------
    # Sidebar (menu)
    st.sidebar.header("💾 Cadastros")
    cultivares = load_cultivares()

    with st.sidebar:
        scroll_navbar(
            anchor_ids,
            anchor_labels=None,
            orientation='vertical'
        )

    st.write(scroll_navbar(anchor_id))

    for anchor_id in anchor_ids:
        st.subheader(anchor_id,anchor=anchor_id)
        
    st.write(scroll_navbar_default)
    for anchor_id in anchor_ids:
        st.subheader(anchor_id,anchor=anchor_id)
        st.write("content " * 100)

if __name__ == "__main__":
    main()
