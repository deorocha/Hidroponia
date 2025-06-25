# produtividade.py

import streamlit as st

col1, col2 = st.columns([10,200])
with col1:
    st.image('./imagens/crescimento.png', width=48)
with col2:
    st.subheader("Crescimento")

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

if __name__ == "__main__":
    main()
