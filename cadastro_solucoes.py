# cadastro_solucoes.py

import streamlit as st
import sqlite3

st.title("🧪 Cadastro Soluções")

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

    # Simulação de interação
    user_input = st.text_input("Digite algo:")
    if user_input:
        st.write(f"📺: Você disse: {user_input}")
        imagem = nome_imagem(user_input)
        st.write(f"📺: Nome da imagem: {imagem}")
        st.image(imagem, caption="Caption da imagem", width=200)

if __name__ == "__main__":
    main()
