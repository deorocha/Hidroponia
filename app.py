import streamlit as st
import pandas as pd
import joblib
import sqlite3

# ------------------------------
# Configurações iniciais
st.set_page_config(
    page_title="Previsão de Nutrientes",
    page_icon=":herb:",
    layout="centered"
)

def load_hydroponics_data():
    conn = sqlite3.connect('hidroponia.db')
    cursor = conn.cursor()
    
    # Carregar dados da tabela tbl_nutrientes
    cursor.execute("SELECT nut_simbolo, nut_nome, nut_tipo, nut_id FROM tbl_nutrientes")
    nutrientes = cursor.fetchall()
    
    # Inicializar listas
    colunas_saida = []
    nomes_completos = []
    ids_nutrientes = []
    macronutrientes = []
    micronutrientes = []
    
    # Processar nutrientes
    for simbolo, nome, tipo, nut_id in nutrientes:
        colunas_saida.append(simbolo)
        nomes_completos.append(nome)
        ids_nutrientes.append(nut_id)
        if tipo == 1:
            macronutrientes.append(simbolo)
        elif tipo == 2:
            micronutrientes.append(simbolo)
    
    # Carregar dados da tabela tbl_cultivar
    cursor.execute("SELECT clt_id, clt_nome FROM tbl_cultivar")
    cultivares = cursor.fetchall()
    
    conn.close()
    
    return {
        'colunas_saida': colunas_saida,
        'nomes_completos': nomes_completos,
        'ids_nutrientes': ids_nutrientes,
        'macronutrientes': macronutrientes,
        'micronutrientes': micronutrientes,
        'cultivares': cultivares
    }

# ------------------------------
# Carregar dados com cache
@st.cache_data
def load_data():
    return load_hydroponics_data()

def load_cultivar_faixas(cultivar_id):
    conn = sqlite3.connect('hidroponia.db')
    cursor = conn.cursor()
    
    # Carregar faixas para todos os nutrientes do cultivar
    cursor.execute(
        """
        SELECT fax_nut_id, fax_minimo, fax_maximo 
        FROM tbl_faixas 
        WHERE fax_clt_id = ?
        """,
        (cultivar_id,)
    )
    
    faixas = cursor.fetchall()
    conn.close()
    
    # Criar dicionário com as faixas por ID do nutriente
    faixa_dict = {}
    for nut_id, minimo, maximo in faixas:
        faixa_dict[nut_id] = (minimo, maximo)
    
    return faixa_dict

# ------------------------------
# 🔧 Definir larguras percentuais das colunas
largura_nome_percent = 40
largura_valor_percent = 20

# ------------------------------
# CSS para responsividade e formatação mobile
st.markdown(f"""
    <style>
    tbody th {{vertical-align: middle;}}
    tbody td {{vertical-align: middle; padding-top: 4px; padding-bottom: 4px;}}
    thead th {{vertical-align: middle; padding-top: 6px; padding-bottom: 6px;}}

    html, body, [class*="css"] {{
        font-size: 15px;
    }}

    table {{
        width: 100% !important;
    }}

    th:nth-child(1), td:nth-child(1) {{
        width: {largura_nome_percent}%;
        word-wrap: break-word;
    }}
    th:nth-child(2), td:nth-child(2) {{
        width: {largura_valor_percent}%;
        text-align: right;
    }}
    th:nth-child(3), td:nth-child(3) {{
        width: {largura_valor_percent}%;
        text-align: right;
    }}
    th:nth-child(4), td:nth-child(4) {{
        width: {largura_valor_percent}%;
        text-align: right;
    }}

    .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }}
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# Título
st.markdown(
    "<h2 style='font-size:26px; font-weight:bold; margin-top:10px;'>🔬 Previsão de Nutrientes na Solução</h2>",
    unsafe_allow_html=True
)
st.write("Preencha os parâmetros para obter a estimativa dos nutrientes.")

# ------------------------------
# Carregar o modelo
@st.cache_data
def carregar_modelo(caminho):
    return joblib.load(caminho)

modelo = carregar_modelo('./hidroponia_modelo.pkl')

data = load_data()
colunas_entrada = ['Temp', 'pH', 'EC', 'O2']
colunas_saida = data['colunas_saida']
nomes_completos = data['nomes_completos']
ids_nutrientes = data['ids_nutrientes']
macronutrientes = data['macronutrientes']
micronutrientes = data['micronutrientes']
cultivares = data['cultivares']

# ------------------------------
# Sidebar (menu)
st.sidebar.header("⚙️ Parâmetros de Entrada")

Temp = st.sidebar.number_input("Temperatura (°C)", min_value=0.0, max_value=50.0, value=25.0, step=0.1)
pH = st.sidebar.number_input("pH", min_value=0.0, max_value=14.0, value=5.5, step=0.1)
EC = st.sidebar.number_input("Condutividade (EC)", min_value=0.0, max_value=10.0, value=1.0, step=0.01)
O2 = st.sidebar.number_input("Oxigênio Dissolvido (O₂)", min_value=0.0, max_value=20.0, value=4.0, step=0.1)

#-------------------------------
# Criar selectbox
cultivar = st.sidebar.selectbox(
    label="Selecione um cultivar:",
    options=range(len(cultivares)),
    format_func=lambda idx: f"{cultivares[idx][1]}",
    index=None,
    help="Selecione um cultivar para configurar a solução nutritiva"
)

if cultivar is not None:
    cultivar_id = cultivares[cultivar][0]
    faixa_dict = load_cultivar_faixas(cultivar_id)
    st.write(f"Cultivar selecionado: {cultivares[cultivar][1]}")

# ------------------------------
# Entrada
entrada = pd.DataFrame([[Temp, pH, EC, O2]],columns=colunas_entrada)

# ------------------------------
# Função de estilo da tabela
def aplicar_estilo(linha):
    idx = linha.name
    simbolo = colunas_saida[idx]
    
    if simbolo in macronutrientes:
        return ['background-color: #E2EFDA'] * len(linha)
    elif simbolo in micronutrientes:
        return ['background-color: #DDEBF7'] * len(linha)
    else:
        return [''] * len(linha)

# ------------------------------
# Botão e previsão
if st.button("🔍 Realizar Previsão"):
    saida = modelo.predict(entrada)[0]

    # Combinar nutriente e símbolo
    nutriente_completo = [f"{nome} ({simbolo})" for nome, simbolo in zip(nomes_completos, colunas_saida)]
    
    if cultivar is not None:
        # Obter valores mínimos e máximos específicos para cada nutriente
        minimos = []
        maximos = []
        for nut_id in ids_nutrientes:
            if nut_id in faixa_dict:
                minimo, maximo = faixa_dict[nut_id]
                minimos.append(minimo)
                maximos.append(maximo)
            else:
                minimos.append(None)
                maximos.append(None)
        
        resultados = pd.DataFrame({
            "Nutriente": nutriente_completo,
            "Valor Previsto": saida,
            "Valor Mínimo": minimo,
            "Valor Máximo": maximo
        })
    else:
        resultados = pd.DataFrame({
            "Nutriente": nutriente_completo,
            "Valor Previsto": saida
        })
    
    # Formatar os valores numéricos
    styled_resultados = (
        resultados
        .style
        .apply(aplicar_estilo, axis=1)
        .format({
            "Valor Previsto": "{:.4f}",
            "Valor Mínimo": "{:.4f}",
            "Valor Máximo": "{:.4f}"
        })
    )

    st.subheader("🧪 Resultados da Previsão")
    # st.markdown(styled_resultados.to_html(), unsafe_allow_html=True)
    st.markdown(styled_resultados.hide(axis="index").to_html(), unsafe_allow_html=True)
    st.success("✅ Previsão realizada com sucesso!")
