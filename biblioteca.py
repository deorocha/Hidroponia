# biblioteca.py

import streamlit as st
import pdfplumber
import re
import os
from PIL import Image, ImageEnhance
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Biblioteca de Conhecimento", layout="wide")
st.title("📚 Biblioteca - Busca Inteligente")

# Arquivo fixo (ajuste o caminho conforme necessário)
PDF_FILE = "./dados/biblioteca.pdf"

def main():
    # Configurações de qualidade
    if 'resolution' not in st.session_state:
        st.session_state.resolution = 300
        
    if 'sharpness' not in st.session_state:
        st.session_state.sharpness = 1.5

    # Função para destacar termos no texto
    def highlight_text(text, search_term):
        if not search_term:
            return text
        
        # Preservar quebras de linha
        lines = text.split('\n')
        highlighted_lines = []
        
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        
        for line in lines:
            highlighted = pattern.sub(
                lambda m: f'<mark style="background-color: #ffff00; font-weight: bold; color: #000;">{m.group(0)}</mark>', 
                line
            )
            highlighted_lines.append(highlighted)
        
        return '<br>'.join(highlighted_lines)

    # Função para processar a estrutura do PDF com cache
    @st.cache_data(ttl=3600, show_spinner=False)
    def extract_pdf_structure(pdf_path):
        if not os.path.exists(pdf_path):
            st.error(f"Arquivo não encontrado: {pdf_path}")
            return [], []
        
        # Extrair todo o texto do PDF com informações de página
        full_text = ""
        page_contents = []
        current_pos = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    # Armazenar conteúdo de cada página com posições
                    start_pos = current_pos
                    end_pos = current_pos + len(text)
                    
                    page_contents.append({
                        "page_num": page_num + 1,
                        "text": text,
                        "start": start_pos,
                        "end": end_pos
                    })
                    
                    full_text += text + "\n\n"
                    current_pos = end_pos + 2  # +2 para as quebras de linha
        
        # Padrão melhorado para identificar perguntas
        qa_pattern = re.compile(
            r'(?:P\.|\?)\s*([^\n?]*[?])',  # Captura texto após "P." ou "?" até encontrar uma quebra de linha ou ?
            re.IGNORECASE
        )
        
        # Encontrar todas as perguntas
        matches = list(qa_pattern.finditer(full_text))
        questions = [{"text": match.group(1).strip(), "start": match.start(), "end": match.end()} 
                     for match in matches]
        
        # Processar respostas
        hierarchy = []
        for i, question in enumerate(questions):
            # Determinar início da resposta (final da pergunta)
            start_pos = question["end"]
            
            # Determinar fim da resposta (início da próxima pergunta ou final do texto)
            if i < len(questions) - 1:
                end_pos = questions[i+1]["start"]
            else:
                end_pos = len(full_text)
            
            # Extrair resposta
            answer = full_text[start_pos:end_pos].strip()
            
            # Limpar a resposta removendo cabeçalhos e prefixos
            answer = re.sub(r'^(P\.\s|\?|R\.\s|Resposta:).*?$', '', answer, flags=re.MULTILINE | re.IGNORECASE)
            answer = re.sub(r'\s+', ' ', answer).strip()
            
            # Encontrar em qual página está a pergunta
            page_num = 1
            for page in page_contents:
                if page["start"] <= question["start"] <= page["end"]:
                    page_num = page["page_num"]
                    break
            
            # Adicionar à hierarquia
            hierarchy.append({
                'type': 'qa',
                'question': question["text"],
                'answer': answer,
                'page': page_num
            })
        
        return [{
            'type': 'topic',
            'text': "Todas as Perguntas e Respostas",
            'page': 1,
            'content': hierarchy
        }], page_contents

    # Função de busca com ordenação por relevância
    def search_in_hierarchy(hierarchy, search_term):
        if not hierarchy or not hierarchy[0]['content']:
            return [], 0
            
        results = []
        search_lower = search_term.lower()
        
        for qa in hierarchy[0]['content']:
            # Buscar tanto na pergunta quanto na resposta
            question_text = qa['question'].lower()
            answer_text = qa['answer'].lower()
            
            if search_lower in question_text or search_lower in answer_text:
                # Calcular relevância baseada na frequência
                relevance = question_text.count(search_lower) * 3 + answer_text.count(search_lower)
                results.append({
                    'node': qa,
                    'relevance': relevance
                })
        
        # Ordenar por relevância
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return [result['node'] for result in results], len(results)

    # Função para gerar imagem de alta qualidade em largura total
    def generate_full_width_image(pdf_path, page_num, resolution=300, sharpness=1.5):
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num - 1]
            
            # Renderizar a página com alta resolução
            img = page.to_image(resolution=resolution).original
            
            # Melhorar a nitidez
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            return img

    # Interface principal
    if os.path.exists(PDF_FILE):
        # Processar PDF com cache
        with st.sidebar:
            with st.spinner("Analisando estrutura do documento..."):
                try:
                    hierarchy, page_contents = extract_pdf_structure(PDF_FILE)
                except Exception as e:
                    st.error(f"Erro ao processar PDF: {str(e)}")
                    st.stop()
        
          ##  if hierarchy and hierarchy[0]['content']:
          ##      st.success(f"Documento processado! {len(hierarchy[0]['content'])} perguntas encontradas.")
          ##  else:
          ##      st.warning("Nenhuma pergunta identificada. Verifique o formato do PDF.")
        
            # Busca
            search_term = st.sidebar.text_input("Buscar conhecimento:", placeholder="Digite um termo ou pergunta...")
        
        if search_term:
            with st.spinner(f"Buscando por '{search_term}'..."):
                results, total_results = search_in_hierarchy(hierarchy, search_term)
            
            if not results:
                st.sidebar.warning("Nenhum resultado encontrado")
            else:
                st.sidebar.success(f"Encontrados {total_results} resultados (ordenados por relevância)")
                
                for i, result in enumerate(results):
                    # Exibir o expander com a pergunta
                    with st.expander(f"**P.{i+1}:** {result['question']} (Página {result['page']})", expanded=False):
                        # Preparar versões destacadas para exibição interna
                        highlighted_question = highlight_text(result['question'], search_term)
                        highlighted_answer = highlight_text(result['answer'], search_term)
                        
                        st.markdown(f"**Pergunta:**<br>{highlighted_question}", unsafe_allow_html=True)
                        st.markdown(f"**Resposta:**<br>{highlighted_answer}", unsafe_allow_html=True)
                        
                        # Renderizar a imagem da página
                      #  try:
                      #      with st.spinner(f"Renderizando página {result['page']} em alta qualidade..."):
                      #          img = generate_full_width_image(
                      #              PDF_FILE, 
                      #              result['page'], 
                      #              resolution=st.session_state.resolution,
                      #              sharpness=st.session_state.sharpness
                      #          )
                      #          
                      #          # Exibir imagem em largura total
                      #          st.image(img, caption=f"Página {result['page']}", use_container_width=True)
                      #          
                      #          # Botão de download abaixo da imagem
                      #          buf = BytesIO()
                      #          img.save(buf, format="JPEG")
                      #          byte_im = buf.getvalue()
                      #          
                      #          st.download_button(
                      #              label=f"⬇️ Baixar imagem da página {result['page']}",
                      #              data=byte_im,
                      #              file_name=f"pagina_{result['page']}.jpg",
                      #              mime="image/jpeg",
                      #              use_container_width=True
                      #          )
                      #          
                      #          st.caption("📝 Dica: Para melhor visualização, use o zoom do navegador (Ctrl + Scroll)")
                      #  except Exception as e:
                      #      st.warning(f"Não foi possível carregar a imagem: {str(e)}")

        # Controles de qualidade na sidebar
        with st.sidebar:
            with st.expander("🔧 Configurações de Qualidade"):
                st.session_state.resolution = st.slider(
                    "Resolução (DPI)", 
                    min_value=150, 
                    max_value=600, 
                    value=300, 
                    step=50
                )
                
                st.session_state.sharpness = st.slider(
                    "Nitidez", 
                    min_value=1.0, 
                    max_value=3.0, 
                    value=1.5, 
                    step=0.1
                )

        # Botão para limpar cache
        if st.sidebar.button("🔄 Limpar cache de processamento", use_container_width=True):
            extract_pdf_structure.clear()
            st.sidebar.success("Cache limpo! O documento será reprocessado.")
            st.rerun()

    else:
        st.error(f"Arquivo não encontrado: {PDF_FILE}")
        st.markdown("""
        **Solução:**
        1. Coloque seu arquivo PDF na mesma pasta deste script
        2. Renomeie-o para `biblioteca.pdf`
        3. Ou ajuste a variável `PDF_FILE` no código
        """)
        st.image("https://via.placeholder.com/600x200?text=Coloque+o+PDF+na+pasta", 
                 use_container_width=True)

if __name__ == "__main__":
    main()
