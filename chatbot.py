import streamlit as st

st.title("🤖 Chatbot")

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

    # Inicializa o histórico de mensagens na sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe as mensagens do histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Recebe a entrada do usuário
    if prompt := st.chat_input("Digite sua mensagem"):
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Exibe a mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)
        # Gera a resposta do bot (aqui, apenas ecoa a mensagem)
        response = prompt
        # Adiciona a resposta do bot ao histórico
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Exibe a resposta do bot
        with st.chat_message("assistant"):
            st.markdown(response)

    # Botão para voltar ao menu principal
#    st.markdown('<a href="/" target="_self"><button style="margin-top:20px;">Voltar ao Menu Principal</button></a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
