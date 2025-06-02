# app.py

import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ------------------------------
# Configurações iniciais
st.set_page_config(page_title="Previsão de Nutrientes", layout="centered")

st.title("🔬 Previsão de Nutrientes na Solução")
st.write("Preencha os valores abaixo para obter a estimativa dos nutrientes.")

# ------------------------------
# Carregar o modelo
@st.cache_data
def carregar_modelo(caminho):
    return joblib.load(caminho)

modelo = carregar_modelo('./hidroponia_modelo.pkl')

# ------------------------------
# Variáveis de entrada
colunas_entrada = ['Temp', 'pH', 'EC', 'O2']
colunas_saida = ['N', 'P', 'K', 'Ca', 'Mg', 'S', 'B', 'Cl', 'Co', 'Cu', 
                  'Fe', 'Mn', 'Mo', 'Na', 'Ni', 'Si', 'Zn']

st.sidebar.header("⚙️ Parâmetros de Entrada")

Temp = st.sidebar.number_input("Temperatura (°C)", min_value=0.0, max_value=35.0, value=25.0, step=0.1)
pH = st.sidebar.number_input("pH", min_value=4.5, max_value=8.0, value=5.5, step=0.1)
EC = st.sidebar.number_input("Condutividade (EC)", min_value=0.0, max_value=8.0, value=1.0, step=0.01)
O2 = st.sidebar.number_input("Oxigênio Dissolvido (O₂)", min_value=0.0, max_value=12.0, value=4.0, step=0.1)

# ------------------------------
# Montar dataframe de entrada
entrada = pd.DataFrame(
    [[Temp, pH, EC, O2]],
    columns=colunas_entrada
)

# ------------------------------
# Botão de previsão
if st.button("🔍 Realizar Previsão"):
    # Fazer a previsão
    saida = modelo.predict(entrada)
    print(saida)

    # Montar dataframe de saída
    resultados = pd.DataFrame(
        data=saida,
        columns=colunas_saida
    ).T.reset_index()

    resultados.columns = ["Nutriente", "Valor Previsto"]

    st.subheader("🧪 Resultados da Previsão")
    st.table(resultados.style.format({"Valor Previsto": "{:.4f}"}))

    st.success("Previsão realizada com sucesso!")
