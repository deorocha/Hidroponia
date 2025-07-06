# crescimento.py

import streamlit as st

# Configuração inicial da página
st.set_page_config(
    page_title="Crescimento",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': None,
        'Get help': None,
        'Report a bug': None
    }
)

# Carregamento do CSS customizado externo
try:
    with open('./styles/style.css') as f:
        css_external = f.read()
    st.markdown(f"<style>{css_external}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Arquivo style.css não encontrado em ./styles/. Verifique o caminho.")
except Exception as e:
    st.error(f"Erro ao carregar style.css: {e}")

def main():
    # Sidebar (menu)
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>📈 Crescimento</h2>",
                    unsafe_allow_html=True)

        # ... Continua o programa ...
        
        # Adiciona espaço para empurrar os botões para o rodapé
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Rodapé do sidebar com os botões
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", key="btn_back_crescimento", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_crescimento", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

if __name__ == "__main__":
    main()
