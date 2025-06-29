import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="👨🏻‍💻 Fórum",
    layout="centered",
    initial_sidebar_state="collapsed"
)

col1, col2 = st.columns([15,200])
with col1:
    st.image('./imagens/forum.png', width=64)
with col2:
    st.subheader("Forum")
st.caption("Troque experiência com outros produtores")

# Carrega o CSS customizado
with open('./styles/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def go_home_standalone():
    st.info("Você está no script 'forum.py'. Para voltar ao menu principal 'HortaTec', você precisaria reiniciar o 'app.py'.")

def main():
    # Sidebar (menu)
    st.sidebar.header("👨🏻‍💻 Fórum")

    #... Continua o programa ...

if __name__ == "__main__":
    main()
