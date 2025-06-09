import streamlit as st
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
# import torch
import re

# --- Configurações ---
SAFE_SOURCE = True
# MODELO DE EMBEDDING: DEVE SER O MESMO QUE EM 'treinar.py'!
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
# Modelo de QA para português (ainda carregado para obter a confiança, mas não para extração de resposta).
QA_MODEL = "pierreguillou/bert-base-cased-squad-v1.1-portuguese"

# --- Funções Auxiliares ---
def preprocess_question(question):
    """
    Prepara a pergunta do usuário para a busca e para o modelo de QA.
    A regex DEVE SER CONSISTENTE com a usada em treinar.py.
    """
    question = question.strip()
    question = re.sub(r'\s+', ' ', question)
    # Mantém letras (incluindo acentuadas), números, espaços, e pontuação essencial
    question = re.sub(r'[^\w\s.,!?;:\-–()\[\]{}<>/=+\*#@&%$\^|~`áéíóúâêîôûàèìòùãõäëïöüçÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÄËÏÖÜÇ]', '', question)
    return question

@st.cache_resource # Armazena os recursos em cache para não recarregar a cada interação
def carregar_recursos():
    """Carrega o modelo de embeddings, o banco de vetores FAISS e o pipeline de QA."""
    try:
        # --- 1. Verificação do diretório FAISS ---
        faiss_index_path = "faiss_index"
        if not os.path.exists(faiss_index_path) or not os.path.isdir(faiss_index_path):
            st.error(f"""
                **Erro: O diretório '{faiss_index_path}' não foi encontrado.**
                Por favor, execute `python treinar.py` primeiro para criar o índice FAISS.
                Certifique-se de que ele esteja no mesmo diretório deste script (`{os.getcwd()}`).
                """)
            st.stop()
        # Verifique se os arquivos essenciais estão dentro da pasta
        if not os.path.exists(os.path.join(faiss_index_path, "index.faiss")) or \
           not os.path.exists(os.path.join(faiss_index_path, "index.pkl")):
            st.error(f"""
                **Erro: Arquivos do índice FAISS (index.faiss ou index.pkl) ausentes ou corrompidos em '{faiss_index_path}'.**
                Por favor, re-execute `python treinar.py` para garantir que o índice seja criado corretamente.
                """)
            st.stop()

        # --- 2. Carregamento do Modelo de Embeddings ---
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        # --- 3. Carregamento do Banco de Vetores FAISS ---
        vector_store = FAISS.load_local(
            faiss_index_path,
            embeddings,
            allow_dangerous_deserialization=SAFE_SOURCE
        )

        # --- 4. Carregamento do Modelo de QA (apenas para obter score de confiança, não para extração) ---
        tokenizer = AutoTokenizer.from_pretrained(QA_MODEL, clean_up_tokenization_spaces=True)
        model = AutoModelForQuestionAnswering.from_pretrained(QA_MODEL)

        # --- 5. Inicialização do Pipeline de QA ---
        device = -1 # if torch.cuda.is_available() else -1
        qa_pipeline = pipeline(
            "question-answering",
            model=model,
            tokenizer=tokenizer,
            device=device
        )
        return vector_store, qa_pipeline
    except Exception as e:
        st.error(f"Erro ao carregar recursos: {e}") # Adicionado para melhor depuração
        st.stop()

vector_store, qa_pipeline = carregar_recursos()

# --- Interface do Streamlit ---
st.title("🤖 ChatBot")
st.markdown("Faça suas perguntas sobre Hidroponia.")

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message.get("content", ""))

def main():

    # Campo de entrada para o usuário
    prompt = st.chat_input("Pergunte algo...")

    if prompt:
        # Adiciona a pergunta do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Buscando e gerando resposta..."):
            try:
                # Pré-processar a pergunta do usuário
                clean_prompt = preprocess_question(prompt)

                # Buscar documentos relevantes no banco de vetores FAISS
                k_docs = 5 # Buscar os 5 chunks mais similares
                docs = vector_store.similarity_search(clean_prompt, k=k_docs)

                if not docs:
                    resposta = "Não consegui encontrar documentos relevantes no PDF para esta pergunta. Tente reformular."
                    confianca = 0.0 # Sem documentos, sem confiança
                    fontes = []
                else:
                    # --- Construir o contexto a partir de TODOS os documentos recuperados ---
                    # Isso dá ao modelo de QA mais informações para extrair a melhor resposta
                    context = " ".join([doc.page_content for doc in docs if doc.page_content.strip()])

                    if not context.strip(): # Fallback caso o contexto esteja vazio (improvável com docs)
                        resposta = "Não consegui extrair um contexto útil dos documentos encontrados. Tente reformular a pergunta."
                        confianca = 0.0
                        fontes = []
                    else:
                        # --- Executar o pipeline de QA para obter a *resposta extraída* e a confiança ---
                        qa_input = {'question': prompt, 'context': context}
                        result = qa_pipeline(qa_input)

                        extracted_answer = result['answer'].strip()
                        confianca = result['score']

                        # --- Prioritize the QA model's extracted answer if it's confident enough ---
                        # If the confidence is low, consider fallback strategies or combining information.
                        if extracted_answer and confianca > 0.3: # Threshold for considering the QA answer "good enough"
                            resposta = extracted_answer
                            # Further refine extracted_answer:
                            # Remove leading prompt if it was extracted by mistake
                            if resposta.lower().startswith(prompt.lower()):
                                resposta = re.sub(r"^" + re.escape(prompt) + r"\s*", "", resposta, count=1, flags=re.IGNORECASE).strip()
                            # Remove "Tópico:" or similar labels if the QA model extracted them
                            resposta = re.sub(r"^(Tópico: .*?\n\n|\w+:\s*)", "", resposta, count=1, flags=re.IGNORECASE).strip()
                            
                            # If after cleaning, the extracted answer is too short or doesn't seem complete,
                            # you might consider appending more from the most relevant source.
                            # This is a heuristic and needs careful tuning.
                            # Example: If extracted_answer is < 50 chars and source 1 is > 100 chars,
                            # it might be useful to append the beginning of source 1.
                            # For now, let's just make sure the `resposta` is the `extracted_answer`.

                        elif docs: # Fallback if QA model isn't confident or no direct answer was extracted
                            # Use the most relevant part of the first document as a fallback.
                            # You might want to summarize it or just take a section.
                            # For simplicity, taking the content of the first doc.
                            # You could also try to generate a summary using another model here.

                            # If `extracted_answer` is empty or confidence is too low,
                            # provide the beginning of the most relevant chunk.
                            resposta = docs[0].page_content.strip()
                            # Clean the fallback response too if it contains "Tópico:" etc.
                            resposta = re.sub(r"^(Tópico: .*?\n\n|\w+:\s*)", "", resposta, count=1, flags=re.IGNORECASE).strip()

                            if not resposta: # If even the first doc is empty after stripping
                                resposta = "Não consegui encontrar uma resposta direta. As fontes podem ajudar."
                            confianca = 0.1 # Lower confidence for fallback

                        else: # No documents found, already handled above, but keeping for clarity
                            resposta = "Não consegui encontrar documentos relevantes no PDF para esta pergunta. Tente reformular."
                            confianca = 0.0

                        fontes = [doc.page_content for doc in docs]

                        # Opcional: Limitar o tamanho da resposta final como um "hard cap"
                        MAX_FINAL_RESPONSE_LENGTH = 1200
                        if len(resposta) > MAX_FINAL_RESPONSE_LENGTH:
                            resposta = resposta[:MAX_FINAL_RESPONSE_LENGTH] + "..."

                        # --- Mensagem final com base na confiança ---
                        if confianca < 0.1:
                            resposta_display = f"{resposta}\n\n*Minha confiança nesta resposta é muito baixa ({confianca*100:.1f}%). Considere reformular a pergunta ou verificar as fontes completas.*"
                        elif confianca < 0.3:
                            resposta_display = f"{resposta}\n\n*(Confiança na resposta: {confianca*100:.1f}%)*"
                        else:
                            resposta_display = resposta

                        resposta = resposta_display
                        st.toast(f"Confiança na resposta: {confianca*100:.1f}%", icon="🤖")

            except Exception as e:
                resposta = "Desculpe, tive um problema ao processar sua pergunta. Tente novamente."
                fontes = []
                st.error(f"**Erro DETALHADO durante a busca ou Geração de Resposta:**\n`{str(e)}`")

        # Exibir a resposta final do assistente
        with st.chat_message("assistant"):
            st.markdown(resposta)
            if fontes:
                with st.expander("🔍 Fontes usadas na resposta"):
                    for i, fonte in enumerate(fontes):
                        st.caption(f"**Fonte {i+1}**:")
                        st.code(fonte, language="text")

if __name__ == '__main__':
   main()
