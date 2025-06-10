# chatbot_app.py
# GEMINI

import streamlit as st
import google.generativeai as genai
import time
import pandas as pd

# --- CONFIGURAÇÕES DA PÁGINA ---
#st.set_page_config(
#    page_title="Chatbot Gemini",
#    page_icon="🤖",
#    layout="wide"
#)

f = open('./chatbot_temas.txt', 'r', encoding='utf-8')
instrucao = f.read()
f.close()

def main():
    # --- CONFIGURAÇÃO DO MODELO GEMINI ---
    try:
        # Configurando a API Key a partir dos secrets do Streamlit
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
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
        # CSS PARA REMOVER BORDA E ESTILIZAR
        st.markdown(
            """
            <style>
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
                {"role": "model", "parts": [{"text": instrucao}]}
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

        st.divider()
        # Configurações avançadas dentro de um expander
        with st.expander("⚙️ **Configurações avançadas**", expanded=False):
            temperature = st.slider("Criatividade", 0.0, 1.0, 0.7, key="temperature")
            max_tokens = st.slider("Comprimento máximo", 100, 4096, 1000, key="max_tokens")

    
    # --- INTERFACE PRINCIPAL DO CHAT ---
    
    st.title("🤖 Chatbot")
    st.caption("Conectado ao Google Gemini 1.5 Flash")
    
    if st.session_state.conversa_atual:
        # Configurações de geração e segurança (com base nos sliders)
        generation_config = {
            "candidate_count": 1,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        safety_settings = {
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL': 'BLOCK_NONE',
            'DANGEROUS': 'BLOCK_NONE'
        }
        
        # Inicializando o modelo com as configurações atuais
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
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

if __name__ == "__main__":
    main()
