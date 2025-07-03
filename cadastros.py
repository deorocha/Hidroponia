# cadastros.py
import streamlit as st
import db_utils
from importlib import import_module

# Configuração inicial da página
st.set_page_config(
    page_title="Cadastros",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': None,
        'Get help': None,
        'Report a bug': None
    }
)

st.subheader("📂 Cadastros")

# CSS para melhorar a aparência
st.markdown("""
    <style>
    .stDataFrame {
        width: 100%;
    }
    .stButton>button {
        width: 100%;
    }
    div[data-baseweb="input"] input {
        background-color: #f0f2f6 !important;
    }
    .stAlert { 
        padding: 10px; 
        border-radius: 5px; 
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

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
page_registry.register_page("bancadas", "cadastro_bancadas", "show")
page_registry.register_page("cultivares", "cadastro_cultivares", "show")
page_registry.register_page("nutrientes", "cadastro_nutrientes", "show")
page_registry.register_page("solucoes", "cadastro_solucoes", "show")
page_registry.register_page("tanques", "cadastro_tanques", "show")
page_registry.register_page("configuracoes", "configuracoes", "show")
page_registry.register_page("sobre", "sobre_nos", "show")
page_registry.register_page("email", "fale_conosco", "show")

def show_sidebar():
    with st.sidebar:
        st.markdown("<div style='font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;'>📂 Navegação</div>", 
                    unsafe_allow_html=True)
        
        st.markdown("<div style='font-weight: bold; margin: 1rem 0 0.5rem 0;'>📁 CADASTROS</div>", 
                    unsafe_allow_html=True)
        
        cols = st.columns(1)
        with cols[0]:
            if st.button("🎍 Bancadas", key="btn_bancadas", use_container_width=True):
                st.session_state.cadastros_page = "bancadas"
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
            if st.button("🚰 Tanques", key="btn_tanques", use_container_width=True):
                st.session_state.cadastros_page = "tanques"
                st.rerun()
        
        st.divider()
        
        st.markdown("<div style='font-weight: bold; margin: 1rem 0 0.5rem 0;'>⚙️ CONFIGURAÇÕES</div>", 
                    unsafe_allow_html=True)
        
        cols = st.columns(1)
        with cols[0]:
            if st.button("⚙️ Configurações", key="btn_config", use_container_width=True):
                st.session_state.cadastros_page = "configuracoes"
                st.rerun()
            if st.button("ℹ️ Sobre nós", key="btn_sobre", use_container_width=True):
                st.session_state.cadastros_page = "sobre"
                st.rerun()
            if st.button("📩 Fale conosco", key="btn_contato", use_container_width=True):
                st.session_state.cadastros_page = "email"
                st.rerun()

def main():
    db_utils.init_db()
    
    if 'cadastros_page' not in st.session_state:
        st.session_state.cadastros_page = "home"
    
    show_sidebar()
    page_registry.show_page(st.session_state.cadastros_page)

if __name__ == "__main__":
    main()
