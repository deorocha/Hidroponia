import streamlit as st
import importlib.util
import sys

# Configuração da página
st.set_page_config(
    page_title="HortaTec",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Sistema de navegação entre páginas
PAGES = {
    "home": "🏠 Menu Principal",
    "calculadora": "🧮 Calculadora",
    "chatbot": "🤖 Chatbot",
    "monitor": "📺 Monitor",
    "graficos": "📊 Gráficos",
    "tabelas": "📋 Tabelas"
}

# CSS personalizado com ícones maiores
st.markdown(
    """
    <style>
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
    }
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }
    .feature-card {
        transition: transform 0.3s;
        text-align: center;
        padding: 25px 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px 0 rgba(0,0,0,0.15);
        background-color: white;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    .feature-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px 0 rgba(0,0,0,0.2);
    }
    .feature-icon {
        font-size: 80px;  /* Tamanho aumentado */
        margin-bottom: 15px;
        line-height: 1;
    }
    .feature-name {
        font-size: 18px;
        font-weight: 600;
        margin-top: 10px;
    }
    .menu-button {
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 100;
    }
    .menu-options {
        position: absolute;
        top: 60px;
        right: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        padding: 10px 0;
        z-index: 100;
        display: none;
        min-width: 150px;
    }
    .menu-option {
        padding: 12px 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 16px;
        transition: background-color 0.2s;
    }
    .menu-option:hover {
        background-color: #f5f5f5;
    }
    .menu-option span {
        font-size: 20px;
    }
    .header-container {
        position: relative;
        margin-bottom: 0px;
        padding-top: 0px;
    }
    .back-button {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 100;
        font-size: 18px;
    }
    @media (max-width: 768px) {
        .features-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    @media (max-width: 480px) {
        .features-grid {
            grid-template-columns: 1fr;
        }
        .feature-icon {
            font-size: 70px;
        }
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
        # Título principal
        st.title("🌱 HortaTec")
        st.markdown("**Soluções inteligentes para agricultura moderna**")
        
        # Botão de menu
        st.markdown(
            """
            <div class="menu-options">
                <div class="menu-option" onclick="handleMenuOption('settings')">
                    <span>⚙️</span> Configurações
                </div>
                <div class="menu-option" onclick="handleMenuOption('print')">
                    <span>🖨️</span> Imprimir
                </div>
                <div class="menu-option" onclick="handleMenuOption('share')">
                    <span>🔗</span> Compartilhar
                </div>
                <div class="menu-option" onclick="handleMenuOption('about')">
                    <span>ℹ️</span> Sobre
                </div>
                <div class="menu-option" onclick="handleMenuOption('exit')">
                    <span>🚪</span> Sair
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.divider()

    # Container centralizado verticalmente
#    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    features = [
        {"icon": "🧮", "name": "Calculadora", "page": "calculadora"},
        {"icon": "🤖", "name": "Chatbot", "page": "chatbot"},
        {"icon": "📺", "name": "Monitor", "page": "monitor"},
        {"icon": "📊", "name": "Gráficos", "page": "graficos"},
        {"icon": "📋", "name": "Tabelas", "page": "tabelas"}
    ]

    # Usar grid para os ícones
    st.markdown('<div class="features-grid">', unsafe_allow_html=True)
    
    for feature in features:
        # Usar botão do Streamlit para garantir a navegação
        if st.button(
            f"{feature['icon']} {feature['name']}",
            key=f"btn_{feature['page']}",
            use_container_width=True
        ):
            st.session_state.current_page = feature['page']
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Fecha features-grid
    st.markdown('</div>', unsafe_allow_html=True)  # Fecha container
    
    # Rodapé
    st.divider()
    st.caption("© 2025 HortaTec | Versão 2.0")
    
    # JavaScript para navegação e menu
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
                    Streamlit.setComponentValue('exit');
                }
            } else {
                alert('Opção selecionada: ' + option);
            }
        }
        
        // Fechar o menu ao clicar fora
        document.addEventListener('click', function(event) {
            const menuButton = document.querySelector('.menu-button');
            const menuOptions = document.querySelector('.menu-options');
            
            if (menuButton && menuOptions) {
                if (!menuButton.contains(event.target) && !menuOptions.contains(event.target)) {
                    menuOptions.style.display = 'none';
                }
            }
        });
        </script>
        """,
        unsafe_allow_html=True
    )

# Sistema de navegação
# Verificar se recebemos um comando de saída
if 'exit' in st.session_state and st.session_state.exit:
    st.success("Obrigado por usar o HortaTec!")
    st.stop()

# Carregar a página atual
if st.session_state.current_page == "home":
    home_page()
else:
    # Adicionar botão de voltar
    if st.button("← Voltar ao Menu", key="btn_back", use_container_width=True):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Espaçamento
    st.write("")
    
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
        if st.button("Voltar ao menu principal", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

