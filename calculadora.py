import streamlit as st
import pandas as pd
import joblib
import sqlite3

# ------------------------------
# Configurações iniciais
#st.set_page_config(
#    page_title="Previsão de Nutrientes",
#    page_icon=":herb:",
#    layout="centered"
#)

def load_hydroponics_data():
    try:
        conn = sqlite3.connect('hidroponia.db')
        cursor = conn.cursor()
        
        # Tenta carregar dados da tabela tbl_nutrientes
        cursor.execute("SELECT nut_simbolo, nut_nome, nut_tipo, nut_id FROM tbl_nutrientes")
        nutrientes = cursor.fetchall()
        
        # Inicializar listas (garante que existirão mesmo sem dados)
        colunas_saida = []
        nomes_completos = []
        ids_nutrientes = []
        macronutrientes = []
        micronutrientes = []
        
        if nutrientes:
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
        cultivares = cursor.fetchall() or []  # Garante lista vazia se None
        
        conn.close()
        
        return {
            'colunas_saida': colunas_saida,
            'nomes_completos': nomes_completos,
            'ids_nutrientes': ids_nutrientes,
            'macronutrientes': macronutrientes,
            'micronutrientes': micronutrientes,
            'cultivares': cultivares
        }
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        # Retorna estruturas vazias em caso de erro
        return {
            'colunas_saida': [],
            'nomes_completos': [],
            'ids_nutrientes': [],
            'macronutrientes': [],
            'micronutrientes': [],
            'cultivares': []
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
        "SELECT fax_nut_id, fax_minimo, fax_maximo FROM tbl_faixas WHERE fax_clt_id = ?",
        (cultivar_id,)
    )
    
    faixas = cursor.fetchall()
    conn.close()
    
    # Criar dicionário com as faixas por ID do nutriente
    faixa_dict = {}
    for nut_id, minimo, maximo in faixas:
        faixa_dict[nut_id] = (nut_id, minimo, maximo)
    
    return faixa_dict

def main():
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
            width: {50}%;
            text-align: left;
            word-wrap: break-word;
        }}
        th:nth-child(2), td:nth-child(2) {{
            width: {15}%;
            text-align: right;
        }}
        th:nth-child(3), td:nth-child(3) {{
            width: {15}%;
            text-align: right;
        }}
        th:nth-child(4), td:nth-child(4) {{
            width: {15}%;
            text-align: right;
        }}
        th:nth-child(5), td:nth-child(5) {{
            width: {5}%;
            text-align: center;
        }}

        .block-container {{
            padding-top: 3rem;
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
    # Verifica se as listas essenciais estão preenchidas
    if not data['ids_nutrientes']:
        st.error("Erro crítico: Não foi possível carregar os IDs dos nutrientes. "
                 "Verifique o banco de dados e a estrutura das tabelas.")
        st.stop()  # Impede a execução do resto do app

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
        accept_new_options=False,
        options=range(len(cultivares)),  # Índices como valores
        format_func=lambda idx: f"{cultivares[idx][1]}",
        index=None,  # Seleciona o primeiro por padrão
        help="Selecione um cultivar para configurar a solução nutritiva"
    )

    if cultivar is not None:
        cultivar_id = cultivares[cultivar][0]
        st.subheader(f"Cultivar: :red[{cultivares[cultivar][1]}]")
        faixa_dict = load_cultivar_faixas(cultivar_id)

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


    # Botão e previsão
    if st.button("🔍 Realizar Previsão"):
        entrada = pd.DataFrame([[Temp, pH, EC, O2]], columns=colunas_entrada)
        saida = modelo.predict(entrada)[0]

        # Combinar nutriente e símbolo
        nutriente = [f"{nome} ({simbolo})" for nome, simbolo in zip(nomes_completos, colunas_saida)]

        if cultivar is not None:
            cultivar_id = cultivares[cultivar][0]
            faixa_dict = load_cultivar_faixas(cultivar_id)

            # Verifica se há dados de faixas para esse cultivar
            if not faixa_dict:
                st.warning("⚠️ Nenhuma faixa definida para este cultivar. Preencha os dados na tabela tbl_faixas.")
                # Exibe apenas os valores previstos formatados com 3 casas
                valores_previstos_formatados = [f"{v:.3f}" for v in saida]
                resultados = pd.DataFrame({
                    "Nutriente": nutriente,
                    "Valor Previsto": valores_previstos_formatados
                })
            else:
                # Obter valores mínimos, máximos e determinar ícones
                minimos = []
                maximos = []
                icones = []
                valores_previstos_formatados = []  # Nome corrigido
                
                for i, nut_id in enumerate(ids_nutrientes):
                    # Verificar se o nutriente existe no dicionário
                    if nut_id in faixa_dict:
                        minimo = faixa_dict[nut_id][1]
                        maximo = faixa_dict[nut_id][2]
                        valor_previsto = saida[i]
                        
                        # Formatar valores com 3 casas decimais
                        valor_formatado = f"{valor_previsto:.3f}"  # Variável temporária
                        minimo_formatado = f"{minimo:.3f}"
                        maximo_formatado = f"{maximo:.3f}"
                        
                        valores_previstos_formatados.append(valor_formatado)
                        minimos.append(minimo_formatado)
                        maximos.append(maximo_formatado)
                        
                        # Determinar o ícone baseado nos valores
                        if valor_previsto < minimo:
                            icones.append('🔻')  # seta para baixo
                        elif valor_previsto > maximo:
                            icones.append('🔺')  # seta para cima
                        else:
                            icones.append('👍')  # like
                    else:
                        # Formatar o valor previsto mesmo sem faixa definida
                        valores_previstos_formatados.append(f"{saida[i]:.3f}")
                        minimos.append("N/A")
                        maximos.append("N/A")
                        icones.append('')  # vazio se não houver dados

                resultados = pd.DataFrame({
                    "Nutriente": nutriente,
                    "Previsto": valores_previstos_formatados,
                    "Mínimo": minimos,
                    "Máximo": maximos,
                    "Status": icones  # Coluna de status com ícones
                })
        else:
            # Caso sem cultivar selecionado: apenas valor previsto formatado
            valores_previstos_formatados = [f"{v:.4f}" for v in saida]
            resultados = pd.DataFrame({
                "Nutriente": nutriente,
                "Valor Previsto": valores_previstos_formatados
            })

        # Aplicar estilo
        styled_resultados = (
            resultados
            .style
            .apply(aplicar_estilo, axis=1)
        )

        st.subheader("🧪 Resultados da Previsão")
        st.markdown(styled_resultados.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.success("✅ Previsão realizada com sucesso!")

if __name__ == "__main__":
    main()
