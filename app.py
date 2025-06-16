import streamlit as st
import importlib.util
import sys

# Configuração da página
st.set_page_config(
    page_title="HortaTec",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sistema de navegação entre páginas
PAGES = {
    "home": "🏠 Menu Principal",
    "calculadora": "🧮 Calculadora",
    "chatbot_gemini": "🤖 Chatbot",
    "monitor": "📺 Agenda de manejo",
    "biblioteca": "📚 Biblioteca",
    "graficos": "📊 Detecção de doenças",
    "tabelas": "📋 Produtividade"
}

# CSS personalizado
st.markdown(
    """
    <style>
    h1 {
        font-size: 2rem; /* Ajuste este valor para o tamanho desejado */
    }
    .block-container {
        padding-top: 2rem; /* Ajuste este valor para diminuir ou aumentar o espaço */
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
    }
    .feature-card {
        transition: transform 0.3s;
        text-align: center;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        margin: 20px auto;
        background-color: white;
        cursor: pointer;
        width: 200px;
    }
    .feature-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    .feature-icon {
        font-size: 70px;
        margin-bottom: 15px;
    }
    .menu-button {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 100;
    }
    .menu-options {
        position: absolute;
        top: 50px;
        right: 10px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        padding: 10px;
        z-index: 100;
        display: none;
    }
    .menu-option {
        padding: 10px 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .menu-option:hover {
        background-color: #f0f0f0;
        border-radius: 5px;
    }
    .header-container {
        position: relative;
        margin-bottom: 50px;
    }
    .back-button {
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 100;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializar o estado da sessão
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# Função para carregar módulos externos
def load_module(module_name):
    """Carrega um módulo externo dinamicamente"""
    spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Página inicial
def home_page():
    """Página inicial com ícones centralizados"""
    # Header com título e botão de menu
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        
        # Título principal
        st.title("🌿 HortaTec")
        
        # Botão de menu
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

    # Container centralizado verticalmente
#    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    features = [
        {"icon": "🧮", "name": "Calculadora", "page": "calculadora"},
        {"icon": "🤖", "name": "Chatbot", "page": "chatbot_gemini"},
        {"icon": "🌱, "name": "Agenda de manejo", "page": "agenda"},
        {"icon": "📚", "name": "Biblioteca", "page": "biblioteca"},
        {"icon": "🐛" "name": "Detecção de doenças", "page": "doencas"},
        {"icon": "📈, "name": "Produtividade", "page": "produtividade"}
    ]
    
    for feature in features:
        # Usar st.link_button para navegação confiável
        if st.button(
            label=f"{feature['icon']} {feature['name']}",
            key=f"btn_{feature['page']}",
            use_container_width=True,
            help=f"Acessar {feature['name']}"
        ):
            st.session_state.current_page = feature['page']
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rodapé
    st.divider()
    st.caption("© 2025 HortaTec | Versão 1.0")
    
    # JavaScript para o menu
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
                    // Envia o comando de saída para o Streamlit
                    Streamlit.setComponentValue('exit');
                }
            } else {
                alert('Opção selecionada: ' + option);
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )

# Sistema de navegação
# Verificar se recebemos um comando de saída
if st.session_state.get('exit', False):
    st.success("Obrigado por usar nosso aplicativo!")
    st.stop()

# Carregar a página atual
if st.session_state.current_page == "home":
    home_page()
else:
    # Adicionar botão de voltar
    if st.button("← Voltar", key="btn_back"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Carregar o módulo correspondente
    try:
        module = load_module(st.session_state.current_page)
        
        # Verificar se o módulo tem uma função main e executá-la
        if hasattr(module, 'main'):
            module.main()
        else:
            st.error(f"O módulo {st.session_state.current_page} não tem uma função 'main' definida")
    except Exception as e:
        st.error(f"Erro ao carregar o módulo {st.session_state.current_page}: {str(e)}")
        if st.button("Voltar ao menu principal"):
            st.session_state.current_page = "home"
            st.rerun()
