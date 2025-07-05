# chatbot_deepseek.py
import streamlit as st
import openai
import time

# Configuração inicial da página
st.set_page_config(
    page_title="ChatBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': None,
        'Get help': None,
        'Report a bug': None
    }
)

st.subheader("🤖 ChatBot")

f = open('./chatbot_temas.txt', 'r', encoding='utf-8')
instrucao = f.read()
f.close()

def main():
    # Botão para voltar ao menu principal
    st.markdown('<a href="/" target="_self"><button style="margin-top:20px;">Voltar ao Menu Principal</button></a>', unsafe_allow_html=True)

    # --- CSS PARA AJUSTAR A LARGURA ---
    st.markdown(
        """
        <style>
            /* Ajusta o container principal */
            .block-container {{
                padding-top: 3rem;
                padding-bottom: 1rem;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }}

            .st-emotion-cache-1f3w014 {{
                height: 2rem;
                width : 2rem;
                background-color: GREEN;
            }}

            /* Container principal do chat */
            [data-testid="stVerticalBlock"]:has([data-testid="stChatMessage"]) {
                padding: 0 5px !important;
            }

            /* Mensagens do chat - layout geral */
            [data-testid="stChatMessage"] {
                width: 100% !important;
                padding: 8px 0 !important;
            }

            /* Balões de mensagem */
            [data-testid="stChatMessageContent"] {
                max-width: 95% !important;
                width: auto !important;
            }

            /* Remover espaçamento entre mensagens */
            [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
                gap: 0 !important;
            }

            /* Área de input */
            [data-testid="stChatInput"] {
                width: 100% !important;
                max-width: 100% !important;
                padding: 10px 0 !important;
            }

            /* Ajustes específicos para dispositivos móveis */
            @media (max-width: 768px) {
                .main .block-container {
                    padding: 0 2px !important;
                }

                [data-testid="stChatMessage"] {
                    padding: 5px 0 !important;
                }

                [data-testid="stChatMessageContent"] {
                    max-width: 98% !important;
                }

                /* Reduz padding das mensagens em mobile */
                .stChatMessage {
                    padding-left: 0.5rem !important;
                    padding-right: 0.5rem !important;
                }

                /* Ajusta o input para mobile */
                [data-testid="stChatInput"] > div {
                    padding: 5px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- CONFIGURAÇÃO DOS MODELOS ---
    DEEPSEEK_CONFIGURADO = False
    OPENAI_CONFIGURADO = False
    
    # Cliente DeepSeek
    client_deepseek = None
    model_name_deepseek = "deepseek-chat"
    
    # Cliente OpenAI
    client_openai = None
    model_name_openai = "gpt-3.5-turbo"  # Modelo padrão da OpenAI
    
    try:
        # Configuração DeepSeek
        client_deepseek = openai.OpenAI(
            api_key=st.secrets["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com/v1",
        )
        DEEPSEEK_CONFIGURADO = True
    except KeyError:
        st.warning("DeepSeek não configurado. Adicione DEEPSEEK_API_KEY em secrets.toml")
    
    try:
        # Configuração OpenAI
        client_openai = openai.OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"],
        )
        OPENAI_CONFIGURADO = True
    except KeyError:
        st.warning("OpenAI não configurada. Adicione OPENAI_API_KEY em secrets.toml")
    
    # Verificar se pelo menos um serviço está configurado
    if not DEEPSEEK_CONFIGURADO and not OPENAI_CONFIGURADO:
        st.error("Nenhum serviço de API configurado. Adicione pelo menos uma chave API.")
        st.stop()

    # --- FUNÇÕES AUXILIARES ---

    def inicializar_estado():
        """Inicializa o estado da sessão do Streamlit."""
        if 'historico_chat' not in st.session_state:
            st.session_state.historico_chat = {}
        if 'conversa_atual' not in st.session_state:
            st.session_state.conversa_atual = None
        if 'mensagens' not in st.session_state:
            st.session_state.mensagens = []
            # Mensagem inicial do sistema para definir o escopo do chatbot
            st.session_state.mensagens.append(
                {"role": "system", "content": instrucao}
            )

    # --- INICIALIZAÇÃO DO ESTADO ---
    inicializar_estado()

    # --- BARRA LATERAL ---
    with st.sidebar:
        # CSS PARA REMOVER BORDA E ESTILIZAR
        st.markdown(
            """
            <style>
            /* Adicione isto para reduzir o espaço acima do botão */
            [data-testid="stSidebar"] > div:first-child > div:first-child {
                padding-top: 0.0rem !important;
                margin-top: 0.0rem !important;
            }

            /* Estilo específico para o botão Nova Conversa */
            [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:first-child button {
                background-color: #0d0d0d !important;
                color: white !important;
                width: 100%;
                border-radius: 8px !important;
                padding: 10px 16px !important;
                text-align: center;
                font-size: 14px;
                font-weight: 500;
                border: none !important;
                box-shadow: none !important;
                transition: background-color 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 12px;
            }

            [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:first-child button:hover {
                background-color: #1a1a1a !important;
            }

            /* Remover todos os efeitos de foco e borda */
            [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:first-child button:focus,
            [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:first-child button:focus-visible,
            [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:first-child button:active {
                outline: none !important;
                box-shadow: none !important;
                border: none !important;
            }

            /* Remover borda interna do Streamlit */
            button.st-emotion-cache-7ym5gk:focus:not(:active) {
                border-color: transparent !important;
                box-shadow: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Botão Nova Conversa
        if st.button("✨ Nova Conversa", key="nova_conversa_btn"):
            id_conversa = f"Conversa_{int(time.time())}"
            st.session_state.conversa_atual = id_conversa
            st.session_state.historico_chat[id_conversa] = [
                {"role": "system", "content": instrucao}
            ]
            st.session_state.mensagens = st.session_state.historico_chat[id_conversa]
            st.rerun()

        st.markdown("---")
        st.subheader("Recentes")

        conversas_ids = list(st.session_state.historico_chat.keys())
        for id_conversa in reversed(conversas_ids):
            conversa = st.session_state.historico_chat[id_conversa]
            # O título da conversa será a primeira pergunta do usuário
            titulo_conversa = id_conversa
            if len(conversa) > 1: # Se houver mais do que a mensagem do sistema
                primeira_mensagem_usuario = next((msg['content'] for msg in conversa if msg['role'] == 'user'), None)
                if primeira_mensagem_usuario:
                    titulo_conversa = f"{primeira_mensagem_usuario[:25]}..." if len(primeira_mensagem_usuario) > 25 else primeira_mensagem_usuario

            with st.expander(titulo_conversa):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("Abrir", key=f"btn_{id_conversa}", use_container_width=True):
                        st.session_state.conversa_atual = id_conversa
                        st.session_state.mensagens = st.session_state.historico_chat[id_conversa]
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{id_conversa}", use_container_width=True):
                        del st.session_state.historico_chat[id_conversa]
                        if st.session_state.conversa_atual == id_conversa:
                            st.session_state.conversa_atual = None
                            st.session_state.mensagens = []
                        st.rerun()

        st.divider()
        with st.expander("⚙️ **Configurações avançadas**", expanded=False):
            temperature = st.slider("Criatividade", 0.0, 1.0, 0.7, key="temperature")
            max_tokens = st.slider("Comprimento máximo", 100, 4096, 2000)
            
            # Seletor de provedor de API
            api_provider = st.selectbox(
                "Provedor de API",
                ["DeepSeek (recomendado)", "OpenAI"],
                index=0
            )


    # --- INTERFACE PRINCIPAL DO CHAT ---

    if st.session_state.conversa_atual:
        # Exibe as mensagens da conversa atual (ignorando a primeira mensagem do sistema)
        for msg in st.session_state.mensagens:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            elif msg["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])

        # Entrada do usuário
        if prompt := st.chat_input("Digite sua mensagem..."):
            if not DEEPSEEK_CONFIGURADO and not OPENAI_CONFIGURADO:
                st.error("Nenhum serviço de API configurado. Verifique suas chaves de API.")
            else:
                with st.chat_message("user"):
                    st.markdown(prompt)
                # Adiciona mensagem do usuário ao histórico local
                st.session_state.mensagens.append({"role": "user", "content": prompt})

                # Envia para a API e exibe a resposta em streaming
                with st.chat_message("assistant"):
                    try:
                        placeholder = st.empty()
                        resposta_completa = ""

                        # Prepara o histórico para a API
                        messages_for_api = []
                        # Inclui a instrução do sistema
                        messages_for_api.append({"role": "system", "content": instrucao})
                        # Adiciona o histórico do chat (últimas 10 mensagens)
                        for msg in st.session_state.mensagens[-10:]:
                            if msg["role"] == "user":
                                messages_for_api.append({"role": "user", "content": msg["content"]})
                            elif msg["role"] == "assistant":
                                messages_for_api.append({"role": "assistant", "content": msg["content"]})

                        # Seleciona o provedor de API baseado na escolha do usuário
                        usar_openai = False
                        client = None
                        model_name = ""
                        
                        # Verifica qual provedor usar
                        if api_provider == "DeepSeek (recomendado)" and DEEPSEEK_CONFIGURADO:
                            client = client_deepseek
                            model_name = model_name_deepseek
                        elif api_provider == "OpenAI" and OPENAI_CONFIGURADO:
                            client = client_openai
                            model_name = model_name_openai
                            usar_openai = True
                        else:
                            # Fallback automático se a primeira opção falhar
                            if DEEPSEEK_CONFIGURADO:
                                client = client_deepseek
                                model_name = model_name_deepseek
                            elif OPENAI_CONFIGURADO:
                                client = client_openai
                                model_name = model_name_openai
                                usar_openai = True

                        # Chama a API com streaming usando o cliente configurado
                        stream = client.chat.completions.create(
                            model=model_name,
                            messages=messages_for_api,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            stream=True,
                        )

                        for chunk in stream:
                            if chunk.choices[0].delta.content is not None:
                                resposta_completa += chunk.choices[0].delta.content
                                placeholder.markdown(resposta_completa + "▌")
                        # Exibe a resposta final sem o cursor
                        placeholder.markdown(resposta_completa)
                        # Adiciona a resposta completa do modelo ao histórico
                        st.session_state.mensagens.append({"role": "assistant", "content": resposta_completa})
                        # Atualiza o histórico da conversa no estado da sessão
                        st.session_state.historico_chat[st.session_state.conversa_atual] = st.session_state.mensagens
                        
                        # Mostra qual provedor foi usado
                        provider = "OpenAI" if usar_openai else "DeepSeek"
                        st.caption(f"Resposta gerada por: {provider}")
                        
                    except openai.NotFoundError:
                        st.error("Modelo ou endpoint não encontrado. Verifique o nome do modelo e a URL da API.")
                    except openai.AuthenticationError:
                        st.error("Falha na autenticação. Verifique sua chave API.")
                    except openai.APIError as api_error:
                        if api_error.status_code == 402:
                            st.warning("Saldo insuficiente no DeepSeek. Recarregue sua conta ou use outro provedor.")
                        else:
                            st.error(f"Erro na API: {str(api_error)}")
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao se comunicar com a API: {str(e)}")

    else:
        st.info("⬅️ Inicie uma nova conversa no menu lateral para começar.")

if __name__ == "__main__":
    main()
