from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import re
import os # Importar os para criar diretórios se necessário

# --- Configurações ---
PDF_PATH = "Questionario_limpo.pdf"
# Ajuste o tamanho e a sobreposição dos chunks conforme a densidade do seu texto.
# 1000-1200 com 200-300 de overlap é um bom ponto de partida para textos informativos.
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 300
# MODELO DE EMBEDDING: ESTE DEVE SER O MESMO EM app.py!
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# --- Funções Auxiliares ---
def clean_text(text):
    """
    Limpeza de texto que normaliza espaços em branco e remove caracteres problemáticos,
    mas MANTÉM a pontuação essencial para a semântica do texto.
    Modelos de QA se beneficiam da pontuação para entender limites de frase e significado.
    """
    # Remove múltiplos espaços em branco, incluindo quebras de linha e quebras de página PDF (\r)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove apenas caracteres que NÃO são:
    # letras (incluindo acentuadas e cedilha), números, espaços,
    # e pontuação essencial (.,;:?!/()-_–'\[\]{}<>/=+\*#@&%$\^|~`\)
    # Esta regex é bem abrangente para português.
    text = re.sub(r'[^\w\s.,;:?!/()\-\–\'\[\]{}<>/=+\*#@&%$\^|~`áéíóúâêîôûàèìòùãõäëïöüçÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÄËÏÖÜÇ]', '', text)
    
    # Remove caracteres que podem ser introduzidos de forma indesejada na leitura do PDF (como \r)
    text = text.replace('\r', '') 
    
    return text.strip()

print(f"Iniciando o treinamento do chatbot com o PDF: {PDF_PATH}")
print(f"Modelo de Embedding utilizado: {EMBEDDING_MODEL}")
print(f"Configuração dos Chunks: Tamanho={CHUNK_SIZE}, Overlap={CHUNK_OVERLAP}")

print("Carregando PDF...")
loader = PyPDFLoader(PDF_PATH)
try:
    pages = loader.load()
    if not pages:
        print("Erro: O PDF parece estar vazio ou não pôde ser carregado. Verifique o caminho e o conteúdo.")
        exit()
    print(f"PDF carregado. Total de páginas: {len(pages)}")
except Exception as e:
    print(f"Erro ao carregar o PDF: {e}")
    print("Certifique-se de que o arquivo PDF existe e não está corrompido.")
    exit()

# Juntar todo o conteúdo antes de dividir
full_text = ""
for page in pages:
    full_text += clean_text(page.page_content) + "\n\n" # Adiciona quebra de linha para separar páginas

print("Dividindo texto em chunks com contexto...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    # Adicionando mais separadores de frase/parágrafo para melhor segmentação
    # Prioriza parágrafos inteiros, depois frases, e então outros separadores.
    separators=["\n\n", ". ", "! ", "? ", "\n", "; ", ": ", ", ", " "] 
)

chunks = text_splitter.split_text(full_text)

if not chunks:
    print("Nenhum chunk foi gerado. Verifique o tamanho do chunk e o conteúdo do texto.")
    exit()

print(f"Número de chunks criados: {len(chunks)}")

# Criar objetos Document para cada chunk
docs = []
for i, chunk in enumerate(chunks):
    docs.append(Document(
        page_content=chunk,
        metadata={"chunk_id": i+1} # Adiciona um metadado simples para identificação
    ))

print("Criando embeddings e salvando no FAISS...")

try:
    # Inicializa o modelo de embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Cria o banco de vetores FAISS a partir dos documentos e embeddings
    vector_store = FAISS.from_documents(docs, embeddings)
    
    # Define o caminho para salvar o índice FAISS
    faiss_index_dir = "faiss_index"
    # Cria o diretório se ele não existir
    if not os.path.exists(faiss_index_dir):
        os.makedirs(faiss_index_dir)
        print(f"Diretório '{faiss_index_dir}' criado.")
        
    # Salva o índice FAISS localmente
    vector_store.save_local(faiss_index_dir)
    
    print("Treinamento concluído e FAISS indexado com sucesso!")

except Exception as e:
    print(f"Erro durante a criação dos embeddings ou salvamento do FAISS: {e}")
    print("Verifique se o modelo de embedding foi baixado corretamente e se há espaço em disco.")
