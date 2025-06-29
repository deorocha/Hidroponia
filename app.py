import streamlit as st
import importlib.util
import sys

# Configuração da página principal do Streamlit
st.set_page_config(
    page_title="HortaTec",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar inicia FECHADO
)

# Oculta os botões do Streamlit
st.markdown(
    r"""
    <style>
        .stAppDeployButton {visibility: hidden;}
        .reportview-container {margin-top: -2em;}
        #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True
)

# Carregamento do CSS customizado externo
try:
    with open('./styles/style.css') as f:
        css_external = f.read()
    # Aplicar globalmente para todas as páginas
    st.markdown(f"<style>{css_external}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Arquivo style.css não encontrado em ./styles/. Verifique o caminho.")
except Exception as e:
    st.error(f"Erro ao carregar style.css: {e}")

# --- Inicializar o estado da sessão ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# --- Função para carregar módulos externos dinamicamente ---
def load_module(module_name):
    """
    Carrega um módulo externo dinamicamente.
    module_name deve ser o nome do arquivo sem a extensão .py (ex: 'agenda').
    """
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

# --- Página inicial (Home) ---
def home_page():
    """Página inicial com ícones centralizados e navegação."""
    
    # --- Sidebar específico da Home ---
    with st.sidebar:
        st.header("Opções Rápidas")
        with st.expander("⚙️ Configurações"):
            st.write("- Opção 1")
            st.write("- Opção 2")
            st.write("- Opção 3")
        with st.expander("ℹ️ Sobre nós..."):
            st.write("- Opção 1")
            st.write("- Opção 2")
            st.write("- Opção 3")
        with st.expander("✉ Contato"):
            st.write("- Opção 1")
            st.write("- Opção 2")
            st.write("- Opção 3")
            
        #if st.button("⚙️ Configurações", key="sidebar_config"):
        #    st.session_state.current_page = "configuracoes"
        #    st.rerun()
        #if st.button("ℹ️ Sobre nós...", key="sidebar_sobre"):
        #    st.session_state.current_page = "sobre_nos"
        #    st.rerun()
        #if st.button("✉ Contato", key="sidebar_contato"):
        #    st.session_state.current_page = "contato"
        #    st.rerun()
        #st.markdown("---")
        #st.markdown("<p style='text-align: center; font-size: 0.8em; color: #888;'>© 2025 HortaTec</p>", unsafe_allow_html=True)


    # Cabeçalho da aplicação (pode conter logo, título e botões de menu)
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        
        # Título principal do aplicativo
        st.title("🌿 HortaTec")
        
        # Bloco para opções de menu (se você tiver um botão que chame toggleMenu no JS)
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

    # Lista de funcionalidades/páginas que serão exibidas como botões
    features = [
        {"icon": "📅", "name": "Agenda de manejo 🚧", "page": "agenda"},
        {"icon": "📚", "name": "Biblioteca 🚧", "page": "biblioteca"},
        {"icon": "📂", "name": "Cadastros", "page": "cadastros"},
        {"icon": "🧮", "name": "Calculadora 🚧", "page": "calculadora"},
        {"icon": "🤖", "name": "Chatbot 🚧", "page": "chatbot_gemini"},
        {"icon": "📈", "name": "Crescimento 🚧", "page": "crescimento"},
        {"icon": "🐛", "name": "Detecção de doenças 🚧", "page": "doencas_imagem"},
        {"icon": "👨🏻‍💻", "name": "Forum 🚧", "page": "forum"},
        {"icon": "📶", "name": "Produtividade 🚧", "page": "produtividade"},
    ]
    
    # Renderiza os botões em uma única coluna vertical
    for feature in features:
        if st.button(
            label=f"{feature['icon']} {feature['name']}",
            key=f"btn_{feature['page']}",
            use_container_width=True # Ocupa a largura do container, que agora será controlada pelo CSS do botão
        ):
            st.session_state.current_page = feature['page']
            st.rerun()

    # Rodapé da página Home
    st.divider()
    st.caption("© 2025 HortaTec | Versão 1.0")
    
    # JavaScript para controlar o menu (se usado)
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
                    // Para realmente sair do app Streamlit via JS, você precisaria de um componente customizado
                }
            } else {
                // alert('Opção selecionada: ' + option);
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )

# --- Sistema de navegação principal (fora das funções de página) ---

if st.session_state.get('exit_app', False):
    st.success("Obrigado por usar nosso aplicativo!")
    st.stop()

if st.session_state.current_page == "home":
    home_page()
else:
    # Adicionar botão de voltar visível em todas as sub-páginas
    if st.button(" ← Voltar ", key="btn_back_universal", help="Retorna à página inicial"):
        st.session_state.current_page = "home"
        st.rerun()
    
    try:
        module = load_module(st.session_state.current_page)
        
        if module and hasattr(module, 'main'):
            module.main()
        elif module:
            st.error(f"O módulo '{st.session_state.current_page}.py' foi carregado, mas não tem uma função 'main()' definida para execução.")
            if st.button("Voltar (Módulo incompleto)", key="error_module_no_main_button_2"):
                st.session_state.current_page = "home"
                st.rerun()
        else:
            if st.button("Voltar (Módulo não encontrado)", key="error_module_load_fail_button_2"):
                st.session_state.current_page = "home"
                st.rerun()
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao tentar exibir o conteúdo da página '{st.session_state.current_page}': {str(e)}")
        if st.button("Voltar (Erro na página)", key="error_page_render_button_2"):
            st.session_state.current_page = "home"
            st.rerun()
