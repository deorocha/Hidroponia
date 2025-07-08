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
        
        /* Novo: Estilos para posicionar o menu no canto superior direito */
        .menu-container {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }
        
        /* Aumentar a largura do menu */
        [data-testid="stSelectbox"] > div {
            width: auto !important;
            min-width: 120px !important;
        }
        
        /* Melhorar a visualização do menu */
        [data-testid="stSelectbox"] > div > div {
            padding: 6px 12px !important;
        }
    </style>
    """, unsafe_allow_html=True
)

# Carregamento do CSS customizado externo
try:
    with open('./styles/style.css') as f:
        css_external = f.read()
    st.markdown(f"<style>{css_external}</style>", unsafe_allow_html=True)
except:
    pass  # Ignora erros de carregamento de CSS

# --- Inicializar estados da sessão ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_id = None
    st.session_state.show_login = True
    st.session_state.show_signup = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# Nova variável para controlar a exibição do formulário de alteração de senha
if 'show_change_password' not in st.session_state:
    st.session_state.show_change_password = False

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
    except:
        return None

# --- Se não está logado, forçar login ---
if not st.session_state.logged_in:
    login_module = load_module("login")
    if login_module and hasattr(login_module, 'main'):
        login_module.main()
    else:
        st.error("Sistema de login não disponível. Contate o suporte.")
    st.stop()

# --- Formulário de Alteração de Senha ---
def change_password_section():
    st.subheader("Alteração de Senha")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Senha Atual", type="password")
        new_password = st.text_input("Nova Senha", type="password")
        confirm_password = st.text_input("Confirmar Nova Senha", type="password")
        submit = st.form_submit_button("Confirmar Alteração")
        
        if submit:
            # Aqui você adicionará a lógica de validação e alteração de senha
            # Por enquanto, vamos apenas verificar se as novas senhas coincidem
            if new_password == confirm_password:
                st.success("Senha alterada com sucesso!")  # Em desenvolvimento, então só mensagem
                st.session_state.show_change_password = False
                st.rerun()
            else:
                st.error("As senhas não coincidem")
    
    if st.button("Cancelar"):
        st.session_state.show_change_password = False
        st.rerun()

# --- Página inicial (Home) ---
def home_page():
    # Container principal
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    
    # Cabeçalho
    col_title, col_menu = st.columns([3, 1])  # Ajustada proporção para 3:1
    
    with col_title:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>🌿 HortaTec</h2>", 
                    unsafe_allow_html=True)
        st.markdown(f"<div class='welcome-message'>Bem-vindo(a), {st.session_state.user_name}!</div>", 
                   unsafe_allow_html=True)
    
    with col_menu:
        # Container para posicionar o menu no canto superior direito
        st.markdown('<div class="menu-container">', unsafe_allow_html=True)
        
        # Botão de menu com a inicial do usuário
        if st.session_state.user_name:
            first_letter = st.session_state.user_name[0].upper()
        else:
            first_letter = "U"
        
        # Menu de opções usando st.selectbox
        menu_options = ["", "Alterar Senha", "Sair"]
        selected_option = st.selectbox(
            "Menu do usuário",
            menu_options,
            index=0,
            format_func=lambda x: f"{first_letter}" if x == "" else x,  # Mostra a inicial do usuário
            label_visibility="collapsed",
            key="user_menu"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)  # Fechar o container do menu
        
        if selected_option == "Alterar Senha":
            st.session_state.show_change_password = True
            st.rerun()
        
        elif selected_option == "Sair":
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_id = None
            st.session_state.current_page = "login"
            st.session_state.show_login = True
            st.rerun()

    # Se estivermos mostrando o formulário de alteração de senha, não exibimos a lista de funcionalidades
    if st.session_state.show_change_password:
        change_password_section()
    else:
        # Lista de funcionalidades
        features = [
            {"icon": "📅", "name": "Agenda de manejo 🚧", "page": "agenda"},
            {"icon": "📚", "name": "Biblioteca", "page": "biblioteca"},
            {"icon": "📂", "name": "Cadastros", "page": "cadastros"},
            {"icon": "🧮", "name": "Calculadora", "page": "calculadora"},
            {"icon": "🤖", "name": "Chatbot", "page": "chatbot_gemini"},
            {"icon": "📈", "name": "Crescimento 🚧", "page": "crescimento"},
            {"icon": "🐛", "name": "Detecção de doenças (modo simulado)", "page": "doencas"},
            {"icon": "📶", "name": "Produtividade 🚧", "page": "produtividade"}
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
    st.caption("© 2025 HortaTec | Versão 1.0")

# --- Sistema de navegação principal ---
if st.session_state.current_page == "home":
    home_page()
else:
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
