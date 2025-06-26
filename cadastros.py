# cadastros.py

import streamlit as st

col1, col2 = st.columns([10,200])
with col1:
    st.image('./imagens/cadastros.png', width=48)
with col2:
    st.subheader("Cadastros")

def main():
    st.markdown(f"""
        <style>
        html, body, [class*="css"] {{
            font-size: 15px;
        }}

        .block-container {{
            padding-top: 3rem;
            padding-bottom: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}
        
        .construction {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3rem !important;
            text-align: center;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Mensagem centralizada com estilo personalizado
    st.markdown(
        '<div class="construction">🚧 Em Construção.</div>', 
        unsafe_allow_html=True
    )

    # Botão para voltar ao menu principal
    st.markdown('<a href="/" target="_self"><button style="margin-top:20px;">Voltar ao Menu Principal</button></a>', unsafe_allow_html=True)

    # ------------------------------
    # Sidebar (menu)
    with st.sidebar:
        st.header("📂 Navegação")
        
        # Categoria Cadastros
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📁 Cadastros</div>', unsafe_allow_html=True)
        if st.button("🎍 Bancadas", key="btn_bancadas", use_container_width=True, 
                     help="Cadastro de bancadas de cultivo"):
            st.switch_page("pages/cadastro_bancadas.py")  # Atualizado
        if st.button("🥬 Cultivares", key="btn_cultivares", use_container_width=True,
                     help="Cadastro de cultivares"):
            st.switch_page("pages/cadastro_cultivares.py")  # Atualizado
        if st.button("🧬 Nutrientes", key="btn_nutrientes", use_container_width=True,
                     help="Cadastro de nutrientes"):
            st.switch_page("pages/cadastro_nutrientes.py")  # Atualizado
        if st.button("🧪 Soluções", key="btn_solucoes", use_container_width=True,
                     help="Cadastro de soluções nutritivas"):
            st.switch_page("pages/cadastro_solucoes.py")  # Atualizado
        if st.button("🚰 Tanques", key="btn_tanques", use_container_width=True,
                     help="Cadastro de tanques"):
            st.switch_page("pages/cadastro_tanques.py")  # Atualizado
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Espaçamento entre seções
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        # Categoria Configurações
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">⚙️ Configurações</div>', unsafe_allow_html=True)
        if st.button("⚙️ Configurações", key="btn_config", use_container_width=True,
                     help="Configurações do sistema"):
            st.switch_page("pages/configuracoes.py")  # Atualizado
        if st.button("ℹ️ Sobre nós...", key="btn_sobre", use_container_width=True,
                     help="Informações sobre a empresa"):
            st.switch_page("pages/sobre.py")  # Atualizado
        if st.button("📩 Fale conosco.", key="btn_contato", use_container_width=True,
                     help="Entre em contato conosco"):
            st.switch_page("pages/email.py")  # Atualizado
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
