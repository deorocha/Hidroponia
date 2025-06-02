# app.py

import streamlit as st
import pandas as pd
import joblib

# ------------------------------
# Configurações iniciais
st.set_page_config(page_title="Previsão de Nutrientes", layout="centered")

# Título com fonte menor
st.markdown(
    "<h2 style='font-size:32px; font-weight:bold;'>🔬 Previsão de Nutrientes na Solução</h2>",
    unsafe_allow_html=True
)
st.write("Preencha os valores abaixo para obter a estimativa dos nutrientes.")

# ------------------------------
# CSS para reduzir altura das linhas
st.markdown("""
    <style>
    tbody th {vertical-align: middle;}
    tbody td {vertical-align: middle; padding-top: 2px; padding-bottom: 2px;}
    thead th {vertical-align: middle; padding-top: 2px; padding-bottom: 2px;}
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# Carregar o modelo
@st.cache_data
def carregar_modelo(caminho):
    return joblib.load(caminho)

modelo = carregar_modelo('hidroponia_modelo.pkl')

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
# Sidebar
st.sidebar.header("⚙️ Parâmetros de Entrada")

Temp = st.sidebar.number_input("Temperatura (°C)", min_value=0.0, max_value=50.0, value=25.0, step=0.1)
pH = st.sidebar.number_input("pH", min_value=0.0, max_value=14.0, value=6.0, step=0.1)
EC = st.sidebar.number_input("Condutividade (EC)", min_value=0.0, max_value=10.0, value=2.0, step=0.01)
O2 = st.sidebar.number_input("Oxigênio Dissolvido (O₂)", min_value=0.0, max_value=20.0, value=8.0, step=0.1)

# ------------------------------
# Entrada
entrada = pd.DataFrame([[Temp, pH, EC, O2]], columns=colunas_entrada)

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

    styled_resultados = resultados.style.apply(aplicar_estilo, axis=1).format({"Valor Previsto": "{:.4f}"})

    st.subheader("🧪 Resultados da Previsão")
    st.table(styled_resultados)
    st.success("Previsão realizada com sucesso!")
