# configuracoes.py

import streamlit as st

def show():
    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/configuracoes.png', width=48)
    with col2:
        st.subheader("Configurações do Sistema")
    
    st.write("Aqui você pode configurar as preferências do sistema:")
    
    # Exemplo de configurações
    with st.expander("Preferências de Visualização"):
        tema = st.selectbox("Tema", ["Claro", "Escuro", "Sistema"])
        densidade = st.select_slider("Densidade da Interface", ["Compacta", "Confortável", "Espaçosa"])
        
        if st.button("Salvar Preferências"):
            st.success("Preferências salvas com sucesso!")
    
    with st.expander("Configurações de Notificação"):
        email = st.text_input("Email para notificações")
        alertas = st.checkbox("Receber alertas por email", True)
        relatorios = st.checkbox("Receber relatórios diários", False)
        
        if st.button("Salvar Configurações de Notificação"):
            st.success("Configurações de notificação salvas!")
    
    with st.expander("Configurações Avançadas"):
        st.warning("⚠️ Alterar essas configurações pode afetar o funcionamento do sistema")
        timeout = st.number_input("Timeout de conexão (segundos)", min_value=5, max_value=60, value=30)
        log_level = st.selectbox("Nível de Log", ["Debug", "Info", "Warning", "Error"])
        
        if st.button("Salvar Configurações Avançadas", type="primary"):
            st.success("Configurações avançadas salvas!")
