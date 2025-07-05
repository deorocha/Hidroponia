import streamlit as st

# Configuração inicial da página
st.set_page_config(
    page_title="Produtividade",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': None,
        'Get help': None,
        'Report a bug': None
    }
)

# Carrega o CSS customizado
with open('./styles/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def go_home_standalone():
    st.info("Você está no script 'produtividade.py'. Para voltar ao menu principal 'HortaTec', você precisaria reiniciar o 'app.py'.")

def main():
    # Sidebar (menu)
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>📶 Produtividade</h2>",
                    unsafe_allow_html=True)

    #... Continua o programa ...

if __name__ == "__main__":
    main()
