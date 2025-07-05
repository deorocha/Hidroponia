import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import joblib
import sqlite3
from PIL import Image
import os

# Configuração inicial da página
st.set_page_config(
    page_title="Calculadora",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': None, 'Get help': None, 'Report a bug': None}
)

# Diretórios de recursos
RESOURCES_DIR = "resources"
CSS_PATH = "./styles/style.css"
JS_PATH = "./scripts/script_calc.js"
IMG_DIR = "./imagens"
DB_NAME = "./dados/hidroponia.db"

# Carregar recursos externos
def load_resources():
    """Carrega CSS, JS e imagens externos"""
    # CSS
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # JS
    if os.path.exists(JS_PATH) and "toggle_js" not in st.session_state:
        with open(JS_PATH) as f:
            st.session_state.toggle_js = f.read()
    
    # Imagens
    if "img_dn" not in st.session_state:
        img_paths = {
            "img_dn": os.path.join(IMG_DIR, "icon_dn.png"),
            "img_up": os.path.join(IMG_DIR, "icon_up.png")
        }
        for key, path in img_paths.items():
            st.session_state[key] = Image.open(path) if os.path.exists(path) else None

# Funções de dados
@st.cache_data
def load_model(path="./modelos/hidroponia_modelo.pkl"):
    """Carrega o modelo ML com cache"""
    return joblib.load(path) if os.path.exists(path) else None

@st.cache_data
def load_db_data():
    """Carrega dados do banco com cache"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT nut_simbolo, nut_nome, nut_tipo, nut_id FROM tbl_nutrientes")
        nutrientes = cursor.fetchall() or []
        
        cursor.execute("SELECT clt_id, clt_nome FROM tbl_cultivares")
        cultivares = cursor.fetchall() or []
        
        # Processar dados
        data = {
            'colunas_saida': [n[0] for n in nutrientes],
            'nomes_completos': [n[1] for n in nutrientes],
            'ids_nutrientes': [n[3] for n in nutrientes],
            'macronutrientes': [n[0] for n in nutrientes if n[2] == 1],
            'micronutrientes': [n[0] for n in nutrientes if n[2] == 2],
            'cultivares': cultivares
        }
        return data
        
    except Exception as e:
        st.error(f"Erro no banco: {str(e)}")
        return {k: [] for k in ['colunas_saida', 'nomes_completos', 'ids_nutrientes', 
                               'macronutrientes', 'micronutrientes', 'cultivares']}

@st.cache_data
def load_cultivar_ranges(cultivar_id):
    """Carrega faixas do cultivar com cache"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT fax_nut_id, fax_minimo, fax_maximo FROM tbl_faixas WHERE fax_clt_id = ?", (cultivar_id,))
        return {nut_id: (minimo, maximo) for nut_id, minimo, maximo in cursor.fetchall()}
    except:
        return {}

# Funções de renderização
def render_sidebar():
    """Renderiza a barra lateral"""
    with st.sidebar:
        st.header("⚙️ Parâmetros de Entrada")
        col1, col2 = st.columns(2)
        
        return {
            'params': {
                'Temp': col1.number_input("Temperatura (°C)", 0.0, 50.0, 25.0, 0.1),
                'pH': col2.number_input("pH", 0.0, 14.0, 5.5, 0.1),
                'EC': col1.number_input("Condutividade (EC)", 0.0, 10.0, 1.0, 0.01),
                'O2': col2.number_input("Oxigênio Dissolvido (O₂)", 0.0, 20.0, 4.0, 0.1),
            },
            'cultivar_idx': st.selectbox(
                "Selecione um cultivar:",
                range(len(st.session_state.cultivares)),
                format_func=lambda i: st.session_state.cultivares[i][1],
                index=None
            ),
            'volume': st.number_input("Volume do tanque (L):", 10, 100000, 1000, 10)
        }

def render_table(df):
    """Renderiza uma tabela estilizada com largura total"""
    # Aplicar classes CSS diretamente
    return f"""
    <div class="full-width-container">
        <div class="scrollable-table">
            {df.to_html(index=False, escape=False)}
        </div>
    </div>
    """

def render_main_results(prediction, cultivar_idx, volume):
    """Renderiza os resultados principais da previsão"""
    # Preparar dados básicos
    nutriente_names = [f"{nome} ({simbolo})" for nome, simbolo in 
                      zip(st.session_state.nomes_completos, st.session_state.colunas_saida)]
    
    # Caso sem cultivar selecionado
    if cultivar_idx is None:
        df = pd.DataFrame({
            "Nutriente": nutriente_names,
            "Valor Previsto": [f"{v:.4f}" for v in prediction]
        })
        st.markdown(render_table(df), unsafe_allow_html=True)
        return None, None
    
    # Com cultivar selecionado
    cultivar_id = st.session_state.cultivares[cultivar_idx][0]
    st.subheader(f"Cultivar: :red[{st.session_state.cultivares[cultivar_idx][1]}]")
    faixas = load_cultivar_ranges(cultivar_id)
    
    if not faixas:
        st.warning("⚠️ Nenhuma faixa definida para este cultivar.")
        df = pd.DataFrame({
            "Nutriente": nutriente_names,
            "Valor Previsto": [f"{v:.4f}" for v in prediction]
        })
        st.markdown(render_table(df), unsafe_allow_html=True)
        return None, None
    
    # Processar resultados com faixas
    resultados, reposicao_abaixo, reposicao_acima = [], [], []
    
    for i, nut_id in enumerate(st.session_state.ids_nutrientes):
        valor = prediction[i]
        valor_fmt = f"{valor:.4f}"
        status, min_fmt, max_fmt = "", "N/A", "N/A"
        
        if nut_id in faixas:
            minimo, maximo = faixas[nut_id]
            min_fmt, max_fmt, med_fmt = f"{minimo:.4f}", f"{maximo:.4f}", f"{(maximo-minimo)/2:.4f}"
            
            if valor < minimo:
                status = "🔻"
                reposicao_g = ((maximo-minimo)/2)-valor #((minimo - valor) * volume) / 1000
                dif_perc = ((((maximo-minimo)/2)-valor) / valor) * 100
                reposicao_abaixo.append({
                    "Nutriente": f"{st.session_state.nomes_completos[i]} ({st.session_state.colunas_saida[i]})",
                    "Valor": valor_fmt,
                    "Mínimo": min_fmt,
                    "Média": med_fmt,
                    "Dif. (%)": f"{dif_perc:.2f}",
                    "Repor (g)*": f"{reposicao_g:.4f}"
                })
            elif valor > maximo:
                status = "🔼"
                reposicao_l = (valor - maximo) * volume / maximo
                reposicao_acima.append({
                    "Nutriente": f"{st.session_state.nomes_completos[i]} ({st.session_state.colunas_saida[i]})",
                    "Valor": valor_fmt,
                    "Máximo": max_fmt,
                    "Repor (L)**": f"{reposicao_l:.4f}"
                })
            else:
                status = "✅"
                
        resultados.append({
            "Nutriente": nutriente_names[i],
            "Previsto": valor_fmt,
            "Mínimo": min_fmt,
            "Máximo": max_fmt,
            "Status": status
        })
    
    # Exibir tabela principal
    st.markdown(render_table(pd.DataFrame(resultados)), unsafe_allow_html=True)
    st.success("✅ Previsão realizada com sucesso!")
    return reposicao_abaixo, reposicao_acima

def render_reposicao_section(title, icon, data, caption):
    """Renderiza uma seção de reposição"""
    with st.container():
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            if icon:
                st.image(icon, width=30)
        with col2:
            st.subheader(title)
        
        if data:
            df = pd.DataFrame(data)
            st.markdown(render_table(df), unsafe_allow_html=True)
            st.caption(caption)

# Função principal
def main():
    # Carregar recursos
    load_resources()
    
    # Título
    st.subheader("🧮 Calculadora de Nutrientes")
    st.write("Preencha os parâmetros à esquerda e clique em 'Realizar Previsão'")
    
    # Inicializar dados essenciais
    if "db_data" not in st.session_state:
        st.session_state.db_data = load_db_data()
        st.session_state.update(st.session_state.db_data)
        st.session_state.model = load_model()
    
    # Obter parâmetros do usuário
    sidebar_data = render_sidebar()
    
    # Processar previsão quando solicitado
    if st.sidebar.button("🔍 Realizar Previsão", use_container_width=True):
        # Executar JS para fechar sidebar
        if "toggle_js" in st.session_state:
            html(f"<script>{st.session_state.toggle_js}</script>")
        
        # Fazer previsão
        try:
            input_data = pd.DataFrame([list(sidebar_data['params'].values())], 
                                     columns=['Temp', 'pH', 'EC', 'O2'])
            prediction = st.session_state.model.predict(input_data)[0]
            
            # Renderizar resultados principais
            reposicao_abaixo, reposicao_acima = render_main_results(
                prediction, 
                sidebar_data['cultivar_idx'], 
                sidebar_data['volume']
            )
            
            # Renderizar seções de reposição
            st.subheader("🧪 Relatório dos Nutrientes")
            
            if reposicao_abaixo:
                render_reposicao_section(
                    "Nutrientes abaixo do mínimo",
                    st.session_state.get("img_dn"),
                    reposicao_abaixo,
                    "* Adicione fertilizantes considerando suas concentrações"
                )
            
            if reposicao_acima:
                render_reposicao_section(
                    "Nutrientes acima do máximo",
                    st.session_state.get("img_up"),
                    reposicao_acima,
                    "** Dilua a solução adicionando água pura"
                )
            
            if not reposicao_abaixo and not reposicao_acima:
                st.info("✅ Todos os nutrientes estão dentro das faixas recomendadas")
                
        except Exception as e:
            st.error(f"Erro na previsão: {str(e)}")

if __name__ == "__main__":
    main()
