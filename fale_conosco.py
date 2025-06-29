# fale_conosco.py

import streamlit as st

def show():
    col1, col2 = st.columns([10,200])
    with col1:
        st.image('./imagens/email.png', width=48)
    with col2:
        st.subheader("Fale Conosco")
    
    st.markdown("""
    ### Envie sua dúvida, sugestão ou feedback
    Nossa equipe está pronta para ajudar você com qualquer questão relacionada ao sistema.
    """)
    
    with st.form(key='contact_form'):
        nome = st.text_input("Nome Completo*", placeholder="Seu nome")
        email = st.text_input("Email*", placeholder="seu.email@exemplo.com")
        assunto = st.selectbox("Assunto*", 
                             ["Dúvida Técnica", "Sugestão", "Relatar Problema", "Elogio", "Outro"])
        
        mensagem = st.text_area("Mensagem*", 
                              placeholder="Descreva sua dúvida, sugestão ou problema...", 
                              height=200)
        
        anexo = st.file_uploader("Anexar arquivo (opcional)", 
                               type=['pdf', 'jpg', 'png', 'txt', 'xlsx'])
        
        termos = st.checkbox("Concordo em compartilhar minhas informações para fins de contato*", value=False)
        
        col1, col2 = st.columns([3,1])
        with col1:
            if st.form_submit_button("📤 Enviar Mensagem"):
                if not nome or not email or not mensagem or not termos:
                    st.error("Por favor, preencha todos os campos obrigatórios (*)")
                else:
                    # Aqui iria a lógica para enviar o email
                    st.success("Mensagem enviada com sucesso! Entraremos em contato em breve.")
                    st.balloons()
        
        with col2:
            st.form_submit_button("🔄 Limpar Formulário", type="secondary")
    
    st.divider()
    st.markdown("### Outras Formas de Contato")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📞 Telefone**")
        st.write("(11) 99999-8888")
        st.write("Horário de atendimento: Seg-Sex, 9h-18h")
        
        st.markdown("**🏢 Endereço**")
        st.write("Av. Paulista, 1000")
        st.write("São Paulo - SP")
        st.write("CEP: 01310-100")
    
    with col2:
        st.markdown("**🌐 Redes Sociais**")
        st.markdown("- [Facebook](https://facebook.com/agrotech)")
        st.markdown("- [Instagram](https://instagram.com/agrotech)")
        st.markdown("- [LinkedIn](https://linkedin.com/company/agrotech)")
        
        st.markdown("**💬 Chat Online**")
        if st.button("Iniciar Chat", key="chat_button"):
            st.info("Nossa equipe de suporte entrará em contato em breve pelo chat.")
