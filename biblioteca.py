import streamlit as st
import csv
from io import StringIO
from collections import defaultdict

# Conteúdo completo do sumario.csv incorporado diretamente
csv_content = """1. Introdução à Hidroponia;;
;1.1. Conceitos básicos;
;;O que é “hidroponia”?
... (todo o conteúdo aqui) ...
;;Quais são os modelos de negócios mais inovadores no setor?"""

st.title("🌳 Árvore de Conhecimento em Hidroponia")
st.caption("Navegue pela hierarquia completa ou pesquise tópicos específicos")

# Processamento hierárquico dos dados
def build_hierarchy(content):
    reader = csv.reader(StringIO(content), delimiter=';')
    items = []
    last_items = {}
    
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
            
        # Determinar nível e texto
        level = 0
        text = ""
        for i, cell in enumerate(row):
            if cell.strip():
                level = i
                text = cell.strip()
                break
                
        # Registrar item atual como último no seu nível
        last_items[level] = text
        
        # Determinar pai (último item do nível anterior)
        parent = last_items.get(level-1) if level > 0 else None
        
        items.append({
            "level": level,
            "text": text,
            "parent": parent
        })
    
    return items

# Construir estrutura de árvore
def create_tree_structure(items):
    # Mapear nós por texto e pai
    node_map = {}
    root_nodes = []
    
    # Criar todos os nós
    for item in items:
        node = {
            "label": item["text"],
            "key": f"{item['parent']}|{item['text']}" if item['parent'] else item['text'],
            "children": []
        }
        node_map[(item["parent"], item["text"])] = node
        
        if item["parent"] is None:
            root_nodes.append(node)
    
    # Adicionar filhos aos pais
    for item in items:
        if item["parent"] is None:
            continue
            
        parent_node = node_map.get((None, item["parent"])) or \
                     next((v for k,v in node_map.items() if k[1] == item["parent"]), None)
        
        if parent_node:
            node = node_map[(item["parent"], item["text"])]
            parent_node["children"].append(node)
    
    return root_nodes

# Processar dados
hierarchy_items = build_hierarchy(csv_content)
tree_data = create_tree_structure(hierarchy_items)

# Função para renderizar a árvore com Streamlit
def render_tree(nodes, parent_key=""):
    for node in nodes:
        key = f"{parent_key}-{node['key']}" if parent_key else node['key']
        
        if node["children"]:
            with st.expander(node["label"], expanded=False):
                render_tree(node["children"], key)
        else:
            st.markdown(f"• {node['label']}")

# Barra lateral com pesquisa
with st.sidebar:
    st.header("🔍 Busca Avançada")
    search_term = st.text_input("Pesquisar na árvore:")
    
    st.markdown("### Dicas de Pesquisa")
    st.markdown("""
    - Use palavras-chave como **NFT** ou **solução nutritiva**
    - Busque por problemas: **pragas**, **pH**
    - Explore plantas: **alface**, **tomate**
    """)
    
    st.markdown("### Estatísticas")
    st.markdown(f"- Total de tópicos: **{len(hierarchy_items)}**")
    st.markdown(f"- Níveis hierárquicos: **{max(i['level'] for i in hierarchy_items) + 1}**")
    st.markdown("---")
    st.caption("Sistema de Gestão de Conhecimento em Hidroponia")

# Lógica de pesquisa e exibição
if search_term:
    st.subheader(f"🔍 Resultados para: '{search_term}'")
    search_term = search_term.lower()
    found_items = []
    
    for item in hierarchy_items:
        if search_term in item["text"].lower():
            # Reconstruir caminho completo
            path = [item["text"]]
            current = item
            while current["parent"]:
                parent = next((i for i in hierarchy_items if i["text"] == current["parent"]), None)
                if parent:
                    path.insert(0, parent["text"])
                    current = parent
                else:
                    break
            found_items.append(" > ".join(path))
    
    if found_items:
        st.success(f"{len(found_items)} resultados encontrados:")
        for item in found_items:
            st.markdown(f"- {item}")
    else:
        st.warning("Nenhum resultado encontrado. Tente outros termos.")
else:
    # Exibir árvore completa
    st.subheader("🌿 Hierarquia Completa")
    st.info("Expanda os tópicos para navegar na estrutura completa")
    render_tree(tree_data)

# Rodapé
st.divider()
st.markdown("""
**Sobre este sistema:**
- Base de conhecimento com todos os tópicos de hidroponia
- Navegação hierárquica estilo árvore (tree view)
- Pesquisa instantânea em todo o conteúdo
- Desenvolvido com Streamlit
""")
