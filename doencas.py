# doencas.py

import streamlit as st

col1, col2 = st.columns([0.25,0.75], gap=None, vertical_alignment="center", border=False)
with col1:
    st.image('./imagens/doencas.png', width=48)
with col2:
    st.subheader("Detecção de doenças")

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
        st.write(f"🐛: Você disse: {user_input}")

    # Botão para voltar ao menu principal
#    st.markdown('<a href="/" target="_self"><button style="margin-top:20px;">Voltar ao Menu Principal</button></a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
