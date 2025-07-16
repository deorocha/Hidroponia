# crescimento.py

import streamlit as st
import sqlite3
import math
import matplotlib.pyplot as plt
import numpy as np
import datetime
import matplotlib.dates as mdates
import pandas as pd
from pandas.api.types import CategoricalDtype

# Configuração inicial da página
st.set_page_config(
    page_title="Crescimento",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': None, 'Get help': None, 'Report a bug': None}
)

custom_html = """
<style>
    .banner {
        width: 100%;
        height: 1px;
        overflow: hidden;
    }
</style>
"""
st.components.v1.html(custom_html)


DB_NAME = "./dados/hidroponia.db"

def calcular_parametros(p_inicial, p_final, dias):
    t0 = dias / 2.0
    K = p_final * 1.05
    tolerancia = 0.01
    max_iter = 1000
    
    for _ in range(max_iter):
        try:
            if K <= p_inicial:
                K = p_inicial * 1.1
                continue
                
            r = -math.log((K / p_inicial) - 1) / (1 - t0)
        except (ValueError, ZeroDivisionError):
            K *= 1.1
            continue
            
        exp_term = math.exp(-r * (dias - t0))
        p_final_calculado = K / (1 + exp_term)
        
        if abs(p_final_calculado - p_final) < tolerancia:
            return K, r, t0
        
        K *= p_final / p_final_calculado
    
    return K, r, t0

def classificar_fase(peso, K):
    if peso < 0.1 * K:
        return "Lenta"
    elif peso < 0.9 * K:
        return "Acelerada"
    else:
        return "Saturação"

def gerar_dados(p_inicial=5.0, p_final=260.0, dias=35):
    try:
        K, r, t0 = calcular_parametros(p_inicial, p_final, dias)
    except Exception as e:
        st.error(f"Erro ao calcular parâmetros: {e}")
        return None, None, None, None, None

    dias_list = list(range(1, dias + 1))
    pesos_list = []
    fases_list = []

    for t in dias_list:
        try:
            exp_term = math.exp(-r * (t - t0))
            peso = K / (1 + exp_term)
            fase = classificar_fase(peso, K)
            pesos_list.append(peso)
            fases_list.append(fase)
        except Exception as e:
            st.error(f"Erro no dia {t}: {e}")
            pesos_list.append(0)
            fases_list.append("Erro")

    return dias_list, pesos_list, fases_list, K, r

def plotar_grafico(dias_list, pesos_list, fases_list, K, p_inicial, p_final, dias, data_inicial, cultivar_nome):
    # Aumentar altura para 6 polegadas
    fig = plt.figure(figsize=(12, 6))
    
    # Adicionar título e subtítulo com espaçamento adequado
    fig.suptitle(
        f"Gráfico de crescimento: {cultivar_nome}",
        fontsize=16,
        fontweight='bold',
        y=0.97  # Posição mais alta
    )
    
    fig.text(
        0.5, 0.90,  # Posicionado logo abaixo do título
        f"Peso inicial: {p_inicial}g   Peso final: {p_final}g   Período: {dias} dias",
        ha='center',
        fontsize=12
    )
    
    ax = fig.add_subplot(111)
    
    # Converter dias numéricos em datas
    datas = [data_inicial + datetime.timedelta(days=d-1) for d in dias_list]
    
    # 1. Define cores de fundo para cada fase
    cores_fundo = {
        "Lenta": (0.85, 0.92, 1.0),      # Azul claro
        "Acelerada": (0.85, 1.0, 0.85),   # Verde claro
        "Saturação": (1.0, 0.9, 0.85)     # Vermelho claro
    }
    
    # 2. Encontra pontos de transição entre as fases
    transicoes = []
    for i in range(1, len(fases_list)):
        if fases_list[i] != fases_list[i-1]:
            transicoes.append((dias_list[i-1] + dias_list[i]) / 2)
    
    # 3. Define limites das áreas
    limites = [dias_list[0] - 0.5] + transicoes + [dias_list[-1] + 0.5]
    
    # Converter limites para datas
    limites_datas = [data_inicial + datetime.timedelta(days=lim-0.5) for lim in limites]
    
    # 4. Pinta as regiões de fundo
    legenda_adicionada = set()
    for i in range(len(limites_datas) - 1):
        # Determina a fase para este intervalo
        idx_fase = next(j for j, dia in enumerate(dias_list) if dia >= limites[i] and dia <= limites[i+1])
        fase_atual = fases_list[idx_fase]
        
        # Adiciona legenda apenas se for a primeira ocorrência da fase
        label = fase_atual if fase_atual not in legenda_adicionada else ""
        if label:
            legenda_adicionada.add(fase_atual)
        
        ax.axvspan(limites_datas[i], limites_datas[i+1], 
                   color=cores_fundo[fase_atual], 
                   alpha=0.4,
                   label=label)
    
    # 5. Divide os dados por fase para plotagem
    fase_lenta_dates = [datas[i] for i, fase in enumerate(fases_list) if fase == "Lenta"]
    fase_lenta_y = [pesos_list[i] for i, fase in enumerate(fases_list) if fase == "Lenta"]
    
    fase_acelerada_dates = [datas[i] for i, fase in enumerate(fases_list) if fase == "Acelerada"]
    fase_acelerada_y = [pesos_list[i] for i, fase in enumerate(fases_list) if fase == "Acelerada"]
    
    fase_saturacao_dates = [datas[i] for i, fase in enumerate(fases_list) if fase == "Saturação"]
    fase_saturacao_y = [pesos_list[i] for i, fase in enumerate(fases_list) if fase == "Saturação"]

    # 6. Linha principal
    ax.plot(datas, pesos_list, 'k-', alpha=0.5, linewidth=2, label='Curva Sigmóide')
    
    # 7. Pontos coloridos por fase
    if fase_lenta_dates:
        ax.plot(fase_lenta_dates, fase_lenta_y, 'bo', markersize=6, label='Fase Lenta')
    if fase_acelerada_dates:
        ax.plot(fase_acelerada_dates, fase_acelerada_y, 'go', markersize=6, label='Fase Acelerada')
    if fase_saturacao_dates:
        ax.plot(fase_saturacao_dates, fase_saturacao_y, 'ro', markersize=6, label='Fase Saturação')

    # Configurações do gráfico
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Peso (g)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Linha horizontal para peso final
    ax.axhline(y=p_final, color='darkorange', linestyle='--', linewidth=1.5, 
               alpha=0.7, label='Peso Final')
    
    # Ponto de inflexão
    if pesos_list:
        idx_meio = min(range(len(pesos_list)), key=lambda i: abs(pesos_list[i] - K/2))
        data_inflexao = datas[idx_meio]
        ax.axvline(x=data_inflexao, color='purple', linestyle=':', linewidth=2,
                  label=f'Infleção ({data_inflexao.strftime("%d/%m/%Y")})')

    # Formatação do eixo X - datas
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    
    # Mostrar todas as datas (1 dia de intervalo)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    
    # Configurações de rotação e tamanho da fonte
    plt.xticks(rotation=90, fontsize=6)
    plt.yticks(fontsize=9)

    # Limites do eixo Y
    ax.set_ylim(0, max(pesos_list) * 1.15)
    
    # Limites do eixo X
    ax.set_xlim(datas[0] - datetime.timedelta(days=0.5), 
               datas[-1] + datetime.timedelta(days=0.5))

    # Legenda
    ax.legend(loc='best', fontsize=9)

    # Ajustar espaçamento - SOLUÇÃO CHAVE
    plt.subplots_adjust(top=0.88, bottom=0.15)
    
    return fig

@st.cache_data
def load_culturas():
    """Carrega dados do banco com cache"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT clt_id, clt_nome, clt_periodo, clt_peso_colheita FROM tbl_cultivares ORDER BY clt_nome")
        cultivare = cursor.fetchall()
        
        # Processar dados
        data = {'cultivares': cultivare}
        return data
    except Exception as e:
        st.error(f"Erro no banco: {str(e)}")
        return {k: [] for k in ['cultivares']}

def main():
    # Inicializar estado da sessão para gráfico
    if 'mostrar_grafico' not in st.session_state:
        st.session_state.mostrar_grafico = False
    if 'dados_grafico' not in st.session_state:
        st.session_state.dados_grafico = None

    # Sidebar (menu)
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>📈 Crescimento</h2>",
                    unsafe_allow_html=True)

        dados_cultivares = load_culturas()

        # Criar lista de nomes e dicionários de mapeamento
        nomes_cultivares = []
        cultivar_id_map = {}
        cultivar_periodo_map = {}
        cultivar_peso_map = {}

        for cultivar in dados_cultivares["cultivares"]:
            clt_id = cultivar[0]
            clt_nome = cultivar[1]
            clt_periodo = cultivar[2]
            clt_peso_colheita = cultivar[3]
            
            nomes_cultivares.append(clt_nome)
            cultivar_id_map[clt_nome] = clt_id
            cultivar_periodo_map[clt_nome] = clt_periodo
            cultivar_peso_map[clt_nome] = clt_peso_colheita

        cultivar_nome = st.selectbox('Cultivar:', placeholder="Selecione um cultivar", options=nomes_cultivares)
        cultivar_id = cultivar_id_map.get(cultivar_nome, None)
        cultivar_periodo = cultivar_periodo_map.get(cultivar_nome, None)
        cultivar_peso = cultivar_peso_map.get(cultivar_nome, None)

        today = datetime.datetime.now()
        
        # Campo Período
        col1_label, col1_field = st.columns([2, 2])
        with col1_label:
            st.markdown("Período (dias):")
        with col1_field:
            periodo_dias = st.number_input("Período:", 0, 140, value=cultivar_periodo, step=1, label_visibility="collapsed")
        
        # Campo Peso esperado
        col2_label, col2_field = st.columns([2, 2])
        with col2_label:
            st.markdown("Peso esperado (g):")
        with col2_field:
            peso_esperado = st.number_input(
                "Peso esperado:", 
                min_value=0.0, 
                max_value=1000.0, 
                value=float(cultivar_peso) if cultivar_peso is not None else 0.0,
                step=1.00,
                format="%.2f",
                label_visibility="collapsed"
            )
        
        # Campo Data do plantio
        col3_label, col3_field = st.columns([2, 2])
        with col3_label:
            st.markdown("Data do plantio:")
        with col3_field:
            data_str = st.text_input("Data do plantio:", 
                                    value=today.strftime("%d/%m/%Y"), 
                                    label_visibility="collapsed")
        
        # Converter para objeto date
        try:
            data_inicial = datetime.datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            st.error("Formato de data inválido! Use dd/mm/yyyy.")
            data_inicial = today.date()

        # Botão para gerar o gráfico
        if st.button("📈 Mostrar Gráfico", use_container_width=True):
            try:
                p_inicial = 5.0
                p_final = peso_esperado
                dias = periodo_dias
                
                # Gerar dados
                dias_list, pesos_list, fases_list, K, r = gerar_dados(p_inicial, p_final, dias)
                
                if dias_list:
                    # Armazenar dados na sessão
                    st.session_state.dados_grafico = {
                        'dias_list': dias_list,
                        'pesos_list': pesos_list,
                        'fases_list': fases_list,
                        'K': K,
                        'p_inicial': p_inicial,
                        'p_final': p_final,
                        'dias': dias,
                        'data_inicial': data_inicial
                    }
                    st.session_state.mostrar_grafico = True
                else:
                    st.error("Não foi possível gerar dados. Verifique os parâmetros.")
            except Exception as e:
                st.error(f"Erro ao gerar dados: {e}")
                st.session_state.mostrar_grafico = False

        # Adiciona espaço para empurrar os botões para o rodapé
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Rodapé do sidebar com os botões
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", key="btn_back_crescimento", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_crescimento", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

    # Área principal - Mostrar o gráfico
    if st.session_state.mostrar_grafico and st.session_state.dados_grafico:
        dados = st.session_state.dados_grafico
        fig = plotar_grafico(
            dados['dias_list'],
            dados['pesos_list'],
            dados['fases_list'],
            dados['K'],
            dados['p_inicial'],
            dados['p_final'],
            dados['dias'],
            dados['data_inicial'],
            cultivar_nome  # Passar o nome do cultivar para o gráfico
        )
        
        # Exibir o gráfico
        st.pyplot(fig)
        
        # Exibir tabela de dados
        st.subheader("Dados de Crescimento")
        
        # Converter dias para datas
        datas = [dados['data_inicial'] + datetime.timedelta(days=d-1) for d in dados['dias_list']]
        
        # Criar DataFrame com os dados
        df = pd.DataFrame({
            'Dia': dados['dias_list'],
            'Data': datas,
            'Fase': dados['fases_list'],
            'Peso (g)': dados['pesos_list']
        })
        
        # Formatar datas para exibição
        df['Data'] = df['Data'].apply(lambda d: d.strftime('%d/%m/%Y'))
        
        # Formatar pesos com 2 casas decimais
        df['Peso (g)'] = df['Peso (g)'].apply(lambda p: f"{p:.2f}")
        
        # Definir ordem das fases para ordenação
        ordem_fases = CategoricalDtype(
            categories=["Lenta", "Acelerada", "Saturação"], 
            ordered=True
        )
        df['Fase'] = df['Fase'].astype(ordem_fases)
        
        # Definir 'Dia' como índice para remover a coluna extra
        df = df.set_index('Dia')
        
        # Exibir tabela sem índice usando st.dataframe
        st.dataframe(df, use_container_width=True)

    else:
        # Mensagem inicial
        st.markdown("""
        <div style="text-align: center; padding: 100px 0;">
            <h2>📈 Simulação de Crescimento</h2>
            <p>Selecione um cultivar e clique em "Mostrar Gráfico" para visualizar a curva de crescimento projetada.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
