# chatbot_ollama.py

import streamlit as st
import requests
import json

# Configurações da API
API_URL = "https://api.together.xyz/v1/chat/completions"

# Modelos serverless disponíveis
AVAILABLE_MODELS = {
    "Mistral 7B Instruct": "mistralai/Mistral-7B-Instruct-v0.1",
    "Mixtral 8x7B Instruct": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "Llama 2 70B Chat": "meta-llama/Llama-2-70b-chat-hf",
    "Nous Hermes 2 Mixtral": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    "CodeLlama 34B Instruct": "codellama/CodeLlama-34b-Instruct-hf"
}

DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

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

st.markdown("""
    <style>
        .block-container {
            margin-top: 1rem;
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Ler instrução do arquivo
try:
    with open('./chatbot_temas.txt', 'r', encoding='utf-8') as f:
        SYSTEM_INSTRUCTION = f.read()
except Exception as e:
    st.error(f"Erro ao ler instruções: {str(e)}")
    SYSTEM_INSTRUCTION = "Você é um assistente prestativo."

# API Key
API_KEY = "d5091edfe2b28cc56a5bc0ad8b2743131d7f31631554a91711c1990359d87bf9"

def main():
    if "model_select" not in st.session_state:
        st.session_state.model_select = DEFAULT_MODEL

    # Sidebar para configurações
    with st.sidebar:
        st.markdown(f"<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>🤖 Chatbot</h2>", unsafe_allow_html=True)
        st.markdown("#### ⚙️ Configurações")
        
        # Seletor de modelo
        selected_model_name = st.selectbox(
            "Selecione o Modelo:",
            options=list(AVAILABLE_MODELS.keys()),
            index=0,
            key="model_selector"
        )
        
        # Atualizar o modelo selecionado na session state
        st.session_state.model_select = AVAILABLE_MODELS[selected_model_name]
        
        # Mostrar qual modelo está sendo usado
        st.info(f"Modelo: {selected_model_name}")
        
        # Configurações do modelo
        max_tokens = st.slider("Tamanho da resposta", 128, 4096, 1024, key="max_tokens_slider")
        temperature = st.slider("Criatividade", 0.0, 1.0, 0.7, key="temperature_slider")
        top_p = st.slider("Foco", 0.0, 1.0, 0.9, key="top_p_slider")
        
        if st.button("🧹 Limpar histórico", key="clear_history_btn", use_container_width=True):
            st.session_state.messages = [
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

    # Inicializar histórico de mensagens SEM a instrução do sistema no histórico
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou especialista em agricultura e hidroponia. Como posso ajudar?"}
        ]

    # Exibir histórico de mensagens
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👨‍🌾"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Processar entrada do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Adicionar mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👨‍🌾"):
            st.markdown(prompt)
        
        # Gerar resposta
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Preparar cabeçalhos e payload
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
                
                # Preparar mensagens para a API - INCLUIR SYSTEM INSTRUCTION CORRETAMENTE
                api_messages = [
                    {"role": "system", "content": SYSTEM_INSTRUCTION}
                ]
                
                # Adicionar histórico de conversa (apenas as últimas 10 mensagens para não exceder o contexto)
                for message in st.session_state.messages[-10:]:
                    api_messages.append(message)
                
                payload = {
                    "model": st.session_state.model_select,
                    "messages": api_messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": True,
                    "stop": ["<|eot_id|>", "<|end_of_text|>", "[INST]", "[/INST]"]
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
                
                # Exibir resposta final
                message_placeholder.markdown(full_response)
            
            except Exception as e:
                error_msg = f"⚠️ **Erro na API:** {str(e)}"
                if "401" in str(e):
                    error_msg += "\n\n🔐 Verifique sua API Key"
                elif "402" in str(e):
                    error_msg += "\n\n💳 Você pode ter excedido seu crédito gratuito"
                elif "400" in str(e) and "non-serverless" in str(e):
                    error_msg += "\n\n🔧 Este modelo requer endpoint dedicado. Tente outro modelo na sidebar."
                elif "rate limit" in str(e).lower():
                    error_msg += "\n\n⏳ Limite de requisições excedido, tente novamente mais tarde"
                
                message_placeholder.markdown(error_msg)
                full_response = error_msg
        
        # Adicionar resposta ao histórico
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
