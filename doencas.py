# doencas.py

import streamlit as st

col1, col2 = st.columns([0.10,0.90], gap=None, vertical_alignment="center", border=False)
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
    """, unsafe_allow_html=True

   import streamlit as st

   enable = st.checkbox("Habilitar a câmera")
   picture = st.camera_input("Tire uma foto", disabled=not enable)

   if picture:
       st.image(picture) 

if __name__ == "__main__":
    main()
