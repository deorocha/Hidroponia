# chatbot_gemini.py

import streamlit as st
import google.generativeai as genai
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

# Carregamento do CSS customizado externo
try:
    with open('./styles/style.css') as f:
        css_external = f.read()
    st.markdown(f"<style>{css_external}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Arquivo style.css não encontrado em ./styles/. Verifique o caminho.")
except Exception as e:
    st.error(f"Erro ao carregar style.css: {e}")

f = open('./chatbot_temas.txt', 'r', encoding='utf-8')
instrucao = f.read()
f.close()

def main():
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
        # model_name='gemini-1.5-flash-latest',
        model = genai.GenerativeModel(
            model_name='gemini-1.5-pro-latest',
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
            # Mensagem inicial do sistema para definir o escopo do chatbot
            st.session_state.mensagens.append(
                {"role": "model", "parts": [{"text": instrucao}]}
            )
    
    # --- INICIALIZAÇÃO DO ESTADO ---
    inicializar_estado()
    
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>🤖 Chatbot</h2>",
            unsafe_allow_html=True)

        # Botão Nova Conversa
        if st.button("✨ Nova Conversa", key="nova_conversa_btn"):
            id_conversa = f"Conversa_{int(time.time())}"
            st.session_state.conversa_atual = id_conversa
            st.session_state.historico_chat[id_conversa] = [
                {"role": "model", "parts": [{"text": instrucao}]}
            ]
            st.session_state.mensagens = st.session_state.historico_chat[id_conversa]
            st.rerun()
            
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

        with st.expander("⚙️ **Configurações avançadas**", expanded=False):
            temperature = st.slider("Criatividade", 0.0, 1.0, 0.7, key="temperature")
            # max_tokens = st.slider("Comprimento máximo", 100, 4096, 1000, key="max_tokens")
            max_tokens = st.slider("Comprimento máximo", 100, 8192, 2000)

        # Adiciona espaço para empurrar os botões para o rodapé
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Rodapé do sidebar com os botões
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", key="btn_back_chatbot", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_chatbot", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

    # --- INTERFACE PRINCIPAL DO CHAT ---
    if st.session_state.conversa_atual:
        # Atualize as configurações com os valores dos sliders
        #generation_config = {
        #    "candidate_count": 1,
        #    "temperature": temperature,  # Valor do slider
        #    "max_output_tokens": max_tokens,  # Valor do slider
        #}
        generation_config = {
            "candidate_count": 1,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,        # Novos parâmetros
            "top_k": 40           # Novos parâmetros
        }
    
        safety_settings = {
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL': 'BLOCK_NONE',
            'DANGEROUS': 'BLOCK_NONE'
        }
    
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # O histórico do Gemini espera 'parts' em vez de 'content'
        # O papel do assistente é 'model'
        #chat = model.start_chat(
        #    history=[
        #        {"role": msg["role"], "parts": msg["parts"]}
        #        for msg in st.session_state.mensagens
        #    ]
        #)
        chat = model.start_chat(
            history=[
                {"role": msg["role"], "parts": msg["parts"]}
                for msg in st.session_state.mensagens[-10:]  # Manter apenas as últimas 10 mensagens
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

if __name__ == "__main__":
    main()
