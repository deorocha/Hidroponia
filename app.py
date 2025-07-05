# app.py

import streamlit as st
import importlib.util
import sys

# Configuração da página principal do Streamlit
st.set_page_config(
    page_title="HortaTec",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Oculta os botões do Streamlit
st.markdown(
    r"""
    <style>
        .stAppDeployButton {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        .reportview-container {margin-top: -2em;}
        #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True
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

# --- Inicializar estados da sessão ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_id = None
    st.session_state.show_login = True  # ESTADO ADICIONADO
    st.session_state.show_signup = False  # ESTADO ADICIONADO

if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

if 'exit_app' not in st.session_state:
    st.session_state.exit_app = False

# --- Verificar se o usuário pediu para sair ---
if st.session_state.exit_app:
    st.success("Obrigado por usar nosso aplicativo! Até logo.")
    st.stop()

# --- Função para carregar módulos externos dinamicamente ---
def load_module(module_name):
    try:
        spec = importlib.util.spec_from_file_location(module_name, f"./{module_name}.py")
        if spec is None:
            raise FileNotFoundError(f"Módulo './{module_name}.py' não encontrado.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except FileNotFoundError as fnfe:
        st.error(f"Erro: Arquivo '{module_name}.py' não encontrado. Verifique o nome e o diretório.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar o módulo {module_name}: {e}")
        return None

# --- Se não está logado, forçar login ---
if not st.session_state.logged_in:
    login_module = load_module("login")
    if login_module and hasattr(login_module, 'main'):
        login_module.main()
    else:
        st.error("Sistema de login não disponível. Contate o suporte.")
    st.stop()

# --- Página inicial (Home) ---
def home_page():
    # Container para o botão Sair no topo da página
    col1, col2, col3 = st.columns([2, 8, 2])
    with col3:
        if st.button("🚪 Sair", key="top_logout", use_container_width=True):
            # Resetar todos os estados de login
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_id = None
            st.session_state.current_page = "login"
            st.session_state.show_login = True
            st.session_state.show_signup = False
            st.rerun()

    with st.sidebar:
        st.header("Opções Rápidas")
        # ... restante do código da sidebar ...
            
        if st.button("🚪 Sair", key="sidebar_logout"):
            # ... código de logout ...
            st.rerun()

    # Cabeçalho da aplicação
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="title-container">', unsafe_allow_html=True)
            st.title(f"🌿 HortaTec - Bem-vindo(a), {st.session_state.user_name}!")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="menu-options">
                <div class="menu-option" onclick="handleMenuOption('settings')">
                    <span>⚙️</span> Settings
                </div>
                <div class="menu-option" onclick="handleMenuOption('print')">
                    <span>🖨️</span> Print
                </div>
                <div class="menu-option" onclick="handleMenuOption('share')">
                    <span>🔗</span> Share
                </div>
                <div class="menu-option" onclick="handleMenuOption('about')">
                    <span>ℹ️</span> About
                </div>
                <div class="menu-option" onclick="handleMenuOption('exit')">
                    <span>🚪</span> Exit
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

    # Lista de funcionalidades
    features = [
        {"icon": "📅", "name": "Agenda de manejo 🚧", "page": "agenda"},
        {"icon": "📚", "name": "Biblioteca", "page": "biblioteca"},
        {"icon": "📂", "name": "Cadastros", "page": "cadastros"},
        {"icon": "🧮", "name": "Calculadora", "page": "calculadora"},
        {"icon": "🤖", "name": "Chatbot", "page": "chatbot_gemini"},
        {"icon": "📈", "name": "Crescimento 🚧", "page": "crescimento"},
        {"icon": "🐛", "name": "Detecção de doenças 🚧", "page": "doencas_imagem"},
        {"icon": "📶", "name": "Produtividade 🚧", "page": "produtividade"},
    ]
    
    for feature in features:
        if st.button(
            label=f"{feature['icon']} {feature['name']}",
            key=f"btn_{feature['page']}",
            use_container_width=True
        ):
            st.session_state.current_page = feature['page']
            st.rerun()

    # Rodapé
    st.divider()
    st.caption("© 2025 HortaTec | Versão 1.0")
    
    st.markdown(
        """
        <script>
        function toggleMenu() {
            const menu = document.querySelector('.menu-options');
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        }
        
        function handleMenuOption(option) {
            const menu = document.querySelector('.menu-options');
            menu.style.display = 'none';
            
            if(option === 'exit') {
                if(confirm('Tem certeza que deseja sair?')) {
                }
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )

# --- Sistema de navegação principal ---
if st.session_state.current_page == "home":
    home_page()
else:
    # Substituir as colunas originais por este novo layout
    col1, spacer, col2 = st.columns([2, 8, 2])
    with col1:
        if st.button(" ← Voltar ", key="btn_back_universal", help="Retorna à página inicial", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    
    with col2:
        if st.button("🚪 Sair", key="btn_logout_universal", use_container_width=True):
            # Resetar todos os estados de login
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_id = None
            st.session_state.current_page = "login"
            st.session_state.show_login = True  # ADICIONADO
            st.session_state.show_signup = False  # ADICIONADO
            st.rerun()
    
    try:
        module = load_module(st.session_state.current_page)
        
        if module and hasattr(module, 'main'):
            module.main()
        elif module:
            st.error(f"O módulo '{st.session_state.current_page}.py' foi carregado, mas não tem uma função 'main()' definida.")
            if st.button("Voltar (Módulo incompleto)", key="error_module_no_main_button_2"):
                st.session_state.current_page = "home"
                st.rerun()
        else:
            if st.button("Voltar (Módulo não encontrado)", key="error_module_load_fail_button_2"):
                st.session_state.current_page = "home"
                st.rerun()
    except Exception as e:
        st.error(f"Erro na página '{st.session_state.current_page}': {str(e)}")
        if st.button("Voltar (Erro na página)", key="error_page_render_button_2"):
            st.session_state.current_page = "home"
            st.rerun()
