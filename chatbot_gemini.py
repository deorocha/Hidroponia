# chatbot_app.py
# GEMINI

import streamlit as st
import google.generativeai as genai
import time

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(
    page_title="Chatbot Gemini",
    page_icon="🤖",
    layout="wide"
)

# --- CONFIGURAÇÃO DO MODELO GEMINI ---
try:
    # Configurando a API Key a partir dos secrets do Streamlit
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Configurações de geração e segurança
    generation_config = {
        "candidate_count": 1,
        "temperature": 0.7,
    }
    safety_settings = {
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL': 'BLOCK_NONE',
        'DANGEROUS': 'BLOCK_NONE'
    }
    # Inicializando o modelo
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest',
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    GEMINI_CONFIGURADO = True
except (KeyError, AttributeError):
    st.error("A GOOGLE_API_KEY não foi encontrada. Por favor, configure-a em .streamlit/secrets.toml")
    GEMINI_CONFIGURADO = False

# --- FUNÇÕES AUXILIARES ---

def inicializar_estado():
    """Inicializa o estado da sessão do Streamlit."""
    if 'historico_chat' not in st.session_state:
        st.session_state.historico_chat = {}
    if 'conversa_atual' not in st.session_state:
        st.session_state.conversa_atual = None
    if 'mensagens' not in st.session_state:
        st.session_state.mensagens = []
        # Mensagem inicial do sistema para dar contexto ao chatbot
        st.session_state.mensagens.append(
            {"role": "model", "parts": [{"text": "Você é um assistente prestativo. Responda em português do Brasil."}]}
        )

# --- INICIALIZAÇÃO DO ESTADO ---
inicializar_estado()

# --- BARRA LATERAL ---
with st.sidebar:
    # CSS para estilizar o st.button
    st.markdown(
        """
        <style>
        .stButton>button {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-start; /* Alinha à esquerda */
            padding: 10px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s;
            background-color: transparent; /* Remove o fundo padrão do botão */
            border: none; /* Remove a borda padrão do botão */
            color: inherit; /* Mantém a cor do texto padrão da sidebar */
            font-size: 18px; /* Tamanho da fonte do texto do botão */
            text-align: left;
        }
        .stButton>button:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        /* Para o ícone dentro do botão, usamos um span com estilo inline ou uma classe aqui */
        .stButton>button .button-icon {
            font-size: 130px; /* Tamanho do ícone maior */
            margin-right: 15px; /* Espaço entre o ícone e o texto */
            line-height: 1; /* Garante que o ícone esteja bem alinhado verticalmente */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Novo botão "Nova Conversa" com ícone e label
    # Usamos HTML dentro do label do botão com st.markdown, se for Streamlit 1.25.0 ou superior,
    # caso contrário, podemos fazer um truque com st.components.v1.html ou apenas o ícone no label.
    # Para simplicidade e compatibilidade, colocaremos o ícone diretamente no label
    # e dependemos do CSS para estilizá-lo se for um span dentro.
    # A maneira mais fácil e compatível:
    # if st.button(f"<span class='button-icon'>✨</span> Nova Conversa", key="nova_conversa_btn", unsafe_allow_html=True):
    if st.button("✨ Nova Conversa", key="nova_conversa_btn"):
        id_conversa = f"Conversa_{int(time.time())}"
        st.session_state.conversa_atual = id_conversa
        # Reinicia o histórico com a mensagem do sistema
        st.session_state.historico_chat[id_conversa] = [
            {"role": "model", "parts": [{"text": "Você é um assistente prestativo. Responda em português do Brasil."}]}
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
            primeira_mensagem_usuario = conversa[1]['parts'][0]['text']
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

# --- INTERFACE PRINCIPAL DO CHAT ---

st.title("🤖 Chatbot")
st.caption("Conectado ao Google Gemini 1.5 Flash")

if st.session_state.conversa_atual:
    # O histórico do Gemini espera 'parts' em vez de 'content'
    # O papel do assistente é 'model'
    chat = model.start_chat(
        history=[
            {"role": msg["role"], "parts": msg["parts"]}
            for msg in st.session_state.mensagens
        ]
    )

    # Exibe as mensagens da conversa atual (ignorando a primeira mensagem do sistema)
    for msg in chat.history[1:]:
        with st.chat_message(msg.role if msg.role == 'user' else 'assistant'):
            st.markdown(msg.parts[0].text)

    # Entrada do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        if not GEMINI_CONFIGURADO:
            st.error("A API do Gemini não está configurada. Verifique o Passo 2.")
        else:
            with st.chat_message("user"):
                st.markdown(prompt)
            # Adiciona mensagem do usuário ao histórico local
            st.session_state.mensagens.append({"role": "user", "parts": [{"text": prompt}]})

            # Envia para o Gemini e exibe a resposta em streaming
            with st.chat_message("assistant"):
                try:
                    placeholder = st.empty()
                    resposta_completa = ""
                    # Chama a API com streaming
                    respostas_stream = chat.send_message(prompt, stream=True)
                    for pedaco in respostas_stream:
                        # Ocasionalmente, um pedaço pode vir vazio
                        if pedaco.text:
                            resposta_completa += pedaco.text
                            placeholder.markdown(resposta_completa + "▌")
                    # Exibe a resposta final sem o cursor
                    placeholder.markdown(resposta_completa)
                    # Adiciona a resposta completa do modelo ao histórico
                    st.session_state.mensagens.append({"role": "model", "parts": [{"text": resposta_completa}]})
                    # Atualiza o histórico da conversa no estado da sessão
                    st.session_state.historico_chat[st.session_state.conversa_atual] = st.session_state.mensagens
                except Exception as e:
                    st.error(f"Ocorreu um erro ao se comunicar com a API do Gemini: {e}")

else:
    st.info("⬅️ Inicie uma nova conversa no menu lateral para começar.")
