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
    """, unsafe_allow_html=True)

    # Inicialização segura do estado da sessão
    if 'photo_taken' not in st.session_state:
        st.session_state.photo_taken = False
        st.session_state.picture = None
        st.session_state.camera_enabled = False

    # Usar o estado da sessão para o checkbox
    enable = st.checkbox("Habilitar a câmera", 
                         value=st.session_state.camera_enabled,
                         key="camera_checkbox")

    # Atualizar o estado interno quando o checkbox mudar
    if enable != st.session_state.camera_enabled:
        st.session_state.camera_enabled = enable
        st.rerun()

    # Lógica principal de exibição
    if st.session_state.photo_taken:
        # Mostrar apenas a foto capturada com largura total
        st.image(st.session_state.picture, use_container_width=True)
        
        if st.button("Tirar nova foto"):
            st.session_state.photo_taken = False
            st.session_state.picture = None
            st.rerun()
    elif st.session_state.camera_enabled:
        # Mostrar apenas a câmera quando habilitada
        picture = st.camera_input("Tire uma foto")
        if picture:
            st.session_state.photo_taken = True
            st.session_state.picture = picture
            st.rerun()

if __name__ == "__main__":
    main()
