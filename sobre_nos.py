# sobre_nos.py

import streamlit as st

def show():
    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/sobre.png', width=48)
    with col2:
        st.subheader("Sobre o Sistema")
    
    st.markdown("""
    ## Hidroponia Inteligente
        
    **Versão:** 2.1.0  
    **Desenvolvedor:** AgroTech Solutions  
    **Última atualização:** 15 de Julho de 2025
    
    ### Nossa Missão
    Fornecer uma solução completa para gestão de sistemas hidropônicos, 
    integrando monitoramento, controle e análise de dados para maximizar 
    a produtividade e eficiência.
    
    ### Recursos Principais
    - Monitoramento em tempo real de parâmetros hidropônicos
    - Controle automatizado de nutrição e irrigação
    - Análise preditiva e recomendações inteligentes
    - Relatórios personalizados e históricos completos
    - Sistema modular e expansível
    
    ### Tecnologias Utilizadas
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        - Python
        - Streamlit
        - SQLite
        - Pandas
        """)
    
    with col2:
        st.markdown("""
        - Matplotlib/Seaborn
        - Scikit-learn
        - TensorFlow Lite
        - IoT Protocols
        """)
    
    with col3:
        st.markdown("""
        - Docker
        - Git
        - CI/CD
        - Cloud Computing
        """)
    
    st.divider()
    st.markdown("### Equipe de Desenvolvimento")
    
    cols = st.columns(4)
    equipe = [
        {"nome": "Carlos Silva", "cargo": "Eng. de Software", "email": "carlos@agrotech.com"},
        {"nome": "Ana Pereira", "cargo": "Cientista de Dados", "email": "ana@agrotech.com"},
        {"nome": "Pedro Santos", "cargo": "Eng. Agrônomo", "email": "pedro@agrotech.com"},
        {"nome": "Mariana Costa", "cargo": "Designer UX/UI", "email": "mariana@agrotech.com"}
    ]
    
    for i, membro in enumerate(equipe):
        with cols[i % 4]:
            st.markdown(f"**{membro['nome']}**")
            st.caption(membro['cargo'])
            st.markdown(f"✉️ {membro['email']}")
