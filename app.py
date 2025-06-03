import streamlit as st
import pandas as pd
import joblib

# ------------------------------
# Configurações iniciais
st.set_page_config(
    page_title="Previsão de Nutrientes",
    page_icon=":herb:",
    layout="centered"
)

# 🔧 Definir larguras percentuais das colunas
largura_nome_percent = 15
largura_simbolo_percent = 30
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
    th:nth-child(3), td:nth-child(3) {{
        width: {largura_simbolo_percent}%;
        text-align: center;
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

# ------------------------------
# Variáveis
colunas_entrada = ['Temp', 'pH', 'EC', 'O2']
colunas_saida = ['N', 'P', 'K', 'Ca', 'Mg', 'S', 'B', 'Cl', 'Co', 'Cu', 
                 'Fe', 'Mn', 'Mo', 'Na', 'Ni', 'Si', 'Zn']

nomes_completos = [
    "Nitrogênio", "Fósforo", "Potássio", "Cálcio", "Magnésio", "Enxofre",
    "Boro", "Cloro", "Cobalto", "Cobre", "Ferro", "Manganês",
    "Molibdênio", "Sódio", "Níquel", "Silício", "Zinco"
]

macronutrientes = ['N', 'P', 'K', 'Ca', 'Mg', 'S']
micronutrientes = ['B', 'Cl', 'Co', 'Cu', 'Fe', 'Mn', 'Mo', 'Na', 'Ni', 'Si', 'Zn']

# ------------------------------
# Sidebar (menu)
st.sidebar.header("⚙️ Parâmetros de Entrada")

Temp = st.sidebar.number_input("Temperatura (°C)", min_value=0.0, max_value=50.0, value=25.0, step=0.1)
pH = st.sidebar.number_input("pH", min_value=0.0, max_value=14.0, value=5.5, step=0.1)
EC = st.sidebar.number_input("Condutividade (EC)", min_value=0.0, max_value=10.0, value=1.0, step=0.01)
O2 = st.sidebar.number_input("Oxigênio Dissolvido (O₂)", min_value=0.0, max_value=20.0, value=4.0, step=0.1)

# ------------------------------
# Entrada
entrada = pd.DataFrame(
    [[Temp, pH, EC, O2]],
    columns=colunas_entrada
)

# ------------------------------
# Função de estilo da tabela
def aplicar_estilo(linha):
    if linha['Símbolo'] in macronutrientes:
        return ['background-color: #E2EFDA'] * len(linha)
    elif linha['Símbolo'] in micronutrientes:
        return ['background-color: #DDEBF7'] * len(linha)
    else:
        return [''] * len(linha)

# ------------------------------
# Botão e previsão
if st.button("🔍 Realizar Previsão"):
    saida = modelo.predict(entrada)[0]

    resultados = pd.DataFrame({
        "Nome do Nutriente": nomes_completos,
        "Símbolo": colunas_saida,
        "Valor Previsto (mg/L)": saida
    })

    # Formatar a exibição para 4 casas decimais (mantendo como float)
    styled_resultados = (
        resultados
        .style
        .apply(aplicar_estilo, axis=1)
        .format({"Valor Previsto (mg/L)": "{:.4f}"})
    )

    st.subheader("🧪 Resultados da Previsão")
    #st.table(styled_resultados)
    st.markdown(styled_resultados.to_html(), unsafe_allow_html=True)
    st.success("✅ Previsão realizada com sucesso!")
