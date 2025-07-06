# cadastros.py

import streamlit as st
import db_utils
from importlib import import_module
import db_utils

# Configuração inicial da página
st.set_page_config(
    page_title="Cadastros",
    page_icon="📂",
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

class PageRegistry:
    def __init__(self):
        self.pages = {}
        self.home_page = None
    
    def register_page(self, page_id, module_name, function_name):
        self.pages[page_id] = (module_name, function_name)
    
    def set_home_page(self, function):
        self.home_page = function
        return function
    
    def show_page(self, page_id):
        if page_id == "home" and self.home_page:
            self.home_page()
        elif page_id in self.pages:
            module_name, function_name = self.pages[page_id]
            try:
                module = import_module(module_name)
                function = getattr(module, function_name)
                function()
            except (ImportError, AttributeError) as e:
                st.error(f"Erro ao carregar a página: {str(e)}")
        else:
            st.error(f"Página '{page_id}' não encontrada")

# Criar o registro de páginas
page_registry = PageRegistry()

# Registrar todas as páginas
page_registry.register_page("estufas", "cadastro_estufas", "show")
page_registry.register_page("bancadas", "cadastro_bancadas", "show")
page_registry.register_page("tanques", "cadastro_tanques", "show")
page_registry.register_page("cultivares", "cadastro_cultivares", "show")
page_registry.register_page("nutrientes", "cadastro_nutrientes", "show")
page_registry.register_page("solucoes", "cadastro_solucoes", "show")

# Definir a página inicial
@page_registry.set_home_page
def home_page():
    st.markdown("""
    <div style='text-align: center; margin-top: 100px;'>
        <h1>📂 Sistema de Cadastros</h1>
        <p>Selecione um dos cadastros no menu lateral para começar</p>
    </div>
    """, unsafe_allow_html=True)

def show_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>📂 Cadastros</h2>",
                    unsafe_allow_html=True)
        
        cols = st.columns(1)
        with cols[0]:
            if st.button("⛺ Estufas", key="btn_estufas", use_container_width=True):
                st.session_state.cadastros_page = "estufas"
                st.rerun()
            if st.button("🎍 Bancadas", key="btn_bancadas", use_container_width=True):
                st.session_state.cadastros_page = "bancadas"
                st.rerun()
            if st.button("🚰 Tanques", key="btn_tanques", use_container_width=True):
                st.session_state.cadastros_page = "tanques"
                st.rerun()
            if st.button("🥬 Cultivares", key="btn_cultivares", use_container_width=True):
                st.session_state.cadastros_page = "cultivares"
                st.rerun()
            if st.button("🧬 Nutrientes", key="btn_nutrientes", use_container_width=True):
                st.session_state.cadastros_page = "nutrientes"
                st.rerun()
            if st.button("🧪 Soluções", key="btn_solucoes", use_container_width=True):
                st.session_state.cadastros_page = "solucoes"
                st.rerun()

        # Adiciona espaço para empurrar os botões para o rodapé
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Rodapé do sidebar com os botões
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", key="btn_back_cadastros", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_cadastros", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

def main():
    db_utils.init_db()
    
    if 'cadastros_page' not in st.session_state:
        st.session_state.cadastros_page = "home"
    
    show_sidebar()
    page_registry.show_page(st.session_state.cadastros_page)

if __name__ == "__main__":
    main()
