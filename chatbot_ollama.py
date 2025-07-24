# chatbot_ollama.py

import streamlit as st
import requests
import json
#import time
# import base64

# Configurações da API
API_URL = "https://api.together.xyz/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/Llama-3-8b-chat-hf"

# Configuração da página
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

# Ler instrução do arquivo
try:
    with open('./chatbot_temas.txt', 'r', encoding='utf-8') as f:
        SYSTEM_INSTRUCTION = f.read()
except Exception as e:
    st.error(f"Erro ao ler instruções: {str(e)}")
    SYSTEM_INSTRUCTION = "Você é um assistente prestativo."

# API Key (mantida fixa)
API_KEY = "d5091edfe2b28cc56a5bc0ad8b2743131d7f31631554a91711c1990359d87bf9"

#def img_to_base64(img_path):
#    with open(img_path, "rb") as f:
#        return base64.b64encode(f.read()).decode()

#chat_png64 = img_to_base64("./imagens/chatbot.png")
#user_png64 = img_to_base64("./imagens/farm.png")

#img_tag_chat = f"<img src='data:image/png;base64,{chat_png64}' style='height:1.5em; vertical-align:middle;'>"
#img_tag_user = f"<img src='data:image/png;base64,{user_png64}' style='height:1.5em; vertical-align:middle;'>"

def main():
    if "model_select" not in st.session_state:
        st.session_state.model_select = DEFAULT_MODEL  # Usa o modelo padrão

    # Sidebar para configurações
    with st.sidebar:
        #st.markdown(f"<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>{img_tag_chat} Chatbot</h2>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>🤖 Chatbot</h2>", unsafe_allow_html=True)
        st.markdown("#### ⚙️ Configurações")
        
        # Configurações do modelo com keys únicas
        model_name = "meta-llama/Llama-3-8b-chat-hf"
        max_tokens = st.slider("Tamanho da resposta", 128, 4096, 1024, key="max_tokens_slider")
        temperature = st.slider("Criatividade", 0.0, 1.0, 0.7, key="temperature_slider")
        top_p = st.slider("Foco", 0.0, 1.0, 0.9,key="top_p_slider")
        
        if st.button("🧹 Limpar histórico", key="clear_history_btn", use_container_width=True):
            st.session_state.messages = [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "assistant", "content": "Histórico limpo! Como posso ajudar com agricultura ou hidroponia?"}
            ]
            st.rerun()
                
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("👈 Voltar", key="btn_back_chatbot", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_chatbot", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

    # Inicializar histórico de mensagens com instrução do sistema
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "assistant", "content": "Olá! Sou especialista em agricultura e hidroponia. Como posso ajudar?"}
        ]

    # Exibir histórico de mensagens (exceto a instrução do sistema)
    for message in st.session_state.messages:
        if message["role"] == "system":  # Não exibir instrução do sistema
            continue

        avatar = "🤖" if message["role"] == "assistant" else "👨‍🌾"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

        #with st.chat_message(message["role"]):
        #    avatar_img = img_tag_chat if message["role"] == "assistant" else img_tag_user
        #    # Exibe o avatar como imagem inline com o texto da mensagem
        #    st.markdown(f"{avatar_img} {message['content']}", unsafe_allow_html=True)

    # Processar entrada do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Adicionar mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👨‍🌾"):
            st.markdown(prompt)
        
        # Gerar resposta com indicador de desempenho
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""
            #start_time = time.time()
            
            try:
                # Preparar cabeçalhos e payload
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
                
                # Incluir instrução do sistema e histórico na requisição
                
                payload = {
                    "model": st.session_state.model_select,
                    "messages": st.session_state.messages,
                    "max_tokens": st.session_state.max_tokens_slider,
                    "temperature": st.session_state.temperature_slider,
                    "top_p": st.session_state.top_p_slider,
                    "stream": True,
                    "stop": ["<|eot_id|>", "<|end_of_text|>"]
                }
                
                # Fazer requisição com streaming
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    stream=True
                )
                
                # Verificar erros na resposta
                if response.status_code != 200:
                    error = response.json().get("error", {}).get("message", "Erro desconhecido")
                    raise Exception(f"Erro na API ({response.status_code}): {error}")
                
                # Processar streaming de resposta
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            json_str = decoded_line[6:]
                            if json_str != '[DONE]':
                                try:
                                    data = json.loads(json_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            token = delta['content']
                                            full_response += token
                                            message_placeholder.markdown(full_response + "▌")
                                except json.JSONDecodeError:
                                    continue
                
                # Calcular métricas de desempenho
                #end_time = time.time()
                #duration = end_time - start_time
                #token_count = len(full_response.split())  # Estimativa simplificada
                #speed = token_count / duration if duration > 0 else 0
                
                # Exibir resposta final com métricas
                message_placeholder.markdown(full_response)
            
            except Exception as e:
                error_msg = f"⚠️ **Erro na API:** {str(e)}"
                if "401" in str(e):
                    error_msg += "\n\n🔐 Verifique sua API Key"
                elif "402" in str(e):
                    error_msg += "\n\n💳 Você pode ter excedido seu crédito gratuito"
                elif "rate limit" in str(e).lower():
                    error_msg += "\n\n⏳ Limite de requisições excedido, tente novamente mais tarde"
                
                message_placeholder.markdown(error_msg)
                full_response = error_msg
        
        # Adicionar resposta ao histórico
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
