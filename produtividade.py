# produtividade.py

import streamlit as st

col1, col2 = st.columns([10,200])
with col1:
    st.image('./imagens/produtividade.png', width=48)
with col2:
    st.subheader("Produtividade")

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
        </style>
    """, unsafe_allow_html=True)

    # Simulação de interação
    user_input = st.text_input("Digite algo:")
    if user_input:
        st.write(f"📶: Você disse: {user_input}")

    # Botão para voltar ao menu principal
#    st.markdown('<a href="/" target="_self"><button style="margin-top:20px;">Voltar ao Menu Principal</button></a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
