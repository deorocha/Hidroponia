"""
    Autor : André Luiz Rocha
    Data  : 05/06/2025 - 07:25
    L.U.  : 22/07/2025 - 00:50
    Programa: crescimento_plotly.py
    Função: Simulação de crescimento sigmoidal com Plotly
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sqlite3
import math
import numpy as np
import datetime
import pandas as pd
import plotly.express as px
from pandas.api.types import CategoricalDtype

# Configurar autorefresh com intervalo seguro
st_autorefresh(interval=1000000, key="datafram_refresh")

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
    /* REMOVER SCROLL VERTICAL DA TABELA */
    div[data-testid="stDataFrame"] div[data-testid="data-container"] > div {
        max-height: none !important;
        overflow-y: hidden !important;
    }
    
    /* REMOVER LIMITES DE ALTURA */
    div[data-testid="stDataFrame"] > div {
        max-height: none !important;
        overflow-y: hidden !important;
    }
    
    div[data-testid="stDataFrame"] {
        max-height: none !important;
        overflow-y: hidden !important;
    }
    
    /* FORÇAR EXIBIÇÃO DE TODAS AS LINHAS */
    div[data-testid="stDataFrame"] table {
        display: table !important;
        height: auto !important;
    }
    
    /* AJUSTES DE ALTURA DAS CÉLULAS */
    div[data-testid="stDataFrame"] th,  
    div[data-testid="stDataFrame"] td {
        padding: 2px 5px !important;
        height: 25px !important;
        line-height: 1.2 !important;
    }
    
    /* REMOVER ESPAÇO INTERNO */
    div[data-testid="stDataFrame"] th > div,
    div[data-testid="stDataFrame"] td > div {
        padding: 0 !important;
        min-height: unset !important;
        height: auto !important;
        line-height: 1.2 !important;
    }
    
    /* AJUSTAR FONTE */
    div[data-testid="stDataFrame"] table {
        font-size: 12px !important;
    }
    
    /* REMOVER ESPAÇO ENTRE LINHAS */
    div[data-testid="stDataFrame"] tr {
        height: 25px !important;
        line-height: 1.2 !important;
    }
</style>
"""
st.components.v1.html(custom_html)

DB_NAME = "./dados/hidroponia.db"

# Dicionário de meses em português
MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

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

def plotar_grafico(dias_list, pesos_list, fases_list, K, p_inicial, p_final, dias, data_inicial, cultivar_nome, pesos_reais=None):
    # Converter data_inicial para datetime.date
    if not isinstance(data_inicial, datetime.date):
        try:
            data_inicial = datetime.datetime.strptime(str(data_inicial), "%Y-%m-%d").date()
        except:
            data_inicial = datetime.date.today()
    
    # Criar lista de datas formatadas como strings
    datas = []
    datas_str = []
    for dia in dias_list:
        try:
            nova_data = data_inicial + datetime.timedelta(days=dia-1)
            datas.append(nova_data)
            datas_str.append(nova_data.strftime('%d/%m/%Y'))
        except:
            datas.append(data_inicial)
            datas_str.append(data_inicial.strftime('%d/%m/%Y'))
    
    # Formatar datas para dd/mmm em português
    dia_texto_list = []
    for d in datas:
        dia = d.day
        mes = MESES_PT[d.month]
        dia_texto_list.append(f"{dia:02d}/{mes}")
    
    # Criar DataFrame com objetos datetime para eixo contínuo
    datas_datetime = pd.to_datetime(datas)
    df = pd.DataFrame({
        'Data': datas_datetime,
        'DataStr': datas_str,
        'Dia': dias_list,
        'Peso (g)': pesos_list,
        'Fase': fases_list,
        'Dia_Texto': dia_texto_list
    })

    # Definir cores para cada fase
    cores_fase = {
        "Lenta": "blue",
        "Acelerada": "green",
        "Saturação": "red"
    }

    # Criar figura com Plotly Express usando datetime no eixo X
    fig = px.scatter(
        df,
        x='Data',
        y='Peso (g)',
        color='Fase',
        color_discrete_map=cores_fase,
        title=f"<b>Gráfico de crescimento: {cultivar_nome}</b><br><sup>Peso inicial: {p_inicial}g   Peso final: {p_final}g   Período: {dias} dias</sup>",
        labels={'Peso (g)': 'Peso (g)', 'Data': 'Data'},
        hover_data={
            'Data': False,
            'DataStr': True,
            'Peso (g)': ':.2f',
            'Dia': False,
            'Fase': False,
            'Dia_Texto': False
        }
    )

    # Adicionar linha sigmoidal (verde)
    fig.add_scatter(
        x=df['Data'],
        y=df['Peso (g)'],
        mode='lines',
        line=dict(color='green', width=2),
        name='Crescimento Previsto',
        hoverinfo='skip'
    )

    # Adicionar linha de crescimento real se houver dados
    if pesos_reais:
        # Filtrar dias com valores reais
        pontos_reais = []
        datas_reais = []
        for i, peso in enumerate(pesos_reais):
            if peso is not None:
                pontos_reais.append(peso)
                datas_reais.append(datas_datetime[i])
        
        # Adicionar pontos reais (vermelhos)
        fig.add_scatter(
            x=datas_reais,
            y=pontos_reais,
            mode='markers',
            marker=dict(
                color='red',
                size=8,
                symbol='diamond'
            ),
            name='Pesos Reais',
            hovertemplate="<b>Data</b>: %{customdata}<br><b>Peso Real (g)</b>: %{y:.2f}<extra></extra>",
            customdata=[d.strftime('%d/%m/%Y') for d in datas_reais],
            # Tooltip com fundo rosa
            hoverlabel=dict(
                bgcolor='#FCE4D6',
                bordercolor='#F8AB9E',
                font_size=10,
                font_family="Arial"
            )
        )
        
        # Adicionar linha conectando os pontos reais (vermelha contínua)
        if len(pontos_reais) > 1:
            fig.add_scatter(
                x=datas_reais,
                y=pontos_reais,
                mode='lines',
                line=dict(color='red', width=2),
                name='Crescimento Real',
                hovertemplate="<b>Data</b>: %{customdata}<br><b>Peso Real (g)</b>: %{y:.2f}<extra></extra>",
                customdata=[d.strftime('%d/%m/%Y') for d in datas_reais],
                # Tooltip com fundo verde claro
                hoverlabel=dict(
                    bgcolor='#92D050',
                    font_size=10,
                    font_family="Arial"
                )
            )

    # Adicionar linhas verticais tracejadas para cada dia usando datetime
    for data in datas_datetime:
        fig.add_vline(
            x=data,
            line_width=1,
            line_dash="dot",
            line_color="gray",
            opacity=0.3
        )

    # Destacar ponto médio (inflexão)
    try:
        idx_meio = min(range(len(pesos_list)), key=lambda i: abs(pesos_list[i] - K/2))
        data_inflexao = datas_datetime[idx_meio]
        
        # Adicionar linha vertical de inflexão
        fig.add_vline(
            x=data_inflexao,
            line_width=2,
            line_dash="dot",
            line_color="purple",
            opacity=0.7,
            annotation_text=f"Infleção ({dia_texto_list[idx_meio]})",
            annotation_position="top right"
        )
    except Exception as e:
        st.write("") # Evitar exibir erro para não interromper a interface

    # Adicionar linha horizontal do peso final
    fig.add_hline(
        y=p_final,
        line_width=2,
        line_dash="dash",
        line_color="darkorange",
        opacity=0.7,
        annotation_text="",
        annotation_position="bottom right"
    )

    # Identificar limites das fases
    fase_lenta = [i for i, fase in enumerate(fases_list) if fase == "Lenta"]
    fase_acelerada = [i for i, fase in enumerate(fases_list) if fase == "Acelerada"]
    fase_saturacao = [i for i, fase in enumerate(fases_list) if fase == "Saturação"]
    
    # Adicionar fundo colorido para cada fase usando datetime
    if fase_lenta:
        fig.add_vrect(
            x0=datas_datetime[0], 
            x1=datas_datetime[fase_lenta[-1]] + pd.Timedelta(days=1),
            fillcolor="#ECF4FA",
            opacity=0.5,
            layer="below",
            line_width=0,
        )
    
    if fase_acelerada:
        fig.add_vrect(
            x0=datas_datetime[fase_acelerada[0]], 
            x1=datas_datetime[fase_acelerada[-1]] + pd.Timedelta(days=1),
            fillcolor="#ECF5E7",
            opacity=0.5,
            layer="below",
            line_width=0,
        )
    
    if fase_saturacao:
        fig.add_vrect(
            x0=datas_datetime[fase_saturacao[0]], 
            x1=datas_datetime[-1] + pd.Timedelta(days=1),
            fillcolor="#FCE4D6",
            opacity=0.5,
            layer="below",
            line_width=0,
        )

    # Configurações de layout
    fig.update_layout(
        hoverlabel=dict(
            bgcolor='rgba(236, 245, 231, 0.8)',
            font_size=10,
            font_family="Arial",
            font_color='black',
            bordercolor='rgba(146, 208, 80, 0.8)'
        ),
        xaxis=dict(
            tickformat="%d/%b",
            type='date',
            title='Data',
            tickfont=dict(family='Arial', size=10),
            tickangle=-90,
            tickmode='array',
            tickvals=datas_datetime,
            ticktext=dia_texto_list
        ),
        yaxis=dict(
            range=[0, max(pesos_list) * 1.15],
            title='Peso (g)',
            tickvals=list(np.arange(0, max(pesos_list) * 1.1, 50))
        ),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        legend_title_text='Fases',
        showlegend=True,
        height=600,
        margin=dict(b=120, t=20, l=20, r=20),
        title_x=0.5,
        title_xanchor='center',
        title_pad=dict(t=0, b=5)
    )

    # Formatação do tooltip
    fig.update_traces(
        hovertemplate="<b>Data</b>: %{customdata[0]}<br><b>Peso (g)</b>: %{y:.2f}<extra></extra>",
        customdata=df[['DataStr']]
    )

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
        conn.close()
        return data
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return {'cultivares': []}

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

        today = datetime.date.today()
        
        # Campo Período
        col1_label, col1_field = st.columns([2, 2])
        with col1_label:
            st.markdown("Período (dias):")
        with col1_field:
            periodo_dias = st.number_input("Período:", 0, 140, value=cultivar_periodo if cultivar_periodo is not None else 35, step=1, label_visibility="collapsed")
        
        # Campo Peso esperado
        col2_label, col2_field = st.columns([2, 2])
        with col2_label:
            st.markdown("Peso esperado (g):")
        with col2_field:
            peso_esperado = st.number_input(
                "Peso esperado:", 
                min_value=0.0, 
                max_value=1000.0, 
                value=float(cultivar_peso) if cultivar_peso is not None else 260.0,
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
            data_inicial = today

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
                        'data_inicial': data_inicial,
                        'cultivar_nome': cultivar_nome,
                        'pesos_reais': [None] * len(dias_list)  # Inicializar pesos reais
                    }
                    st.session_state.mostrar_grafico = True
                    # Inicializar pesos reais temporários
                    st.session_state.temp_pesos_reais = [None] * len(dias_list)
                else:
                    st.error("Não foi possível gerar dados. Verifique os parâmetros.")
            except Exception as e:
                st.error(f"Erro ao gerar dados: {e}")
                st.session_state.mostrar_grafico = False

        # Adiciona espaço para empurrar os botões para o rodapé
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Rodapé do sidebar com os botões
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
        
        try:
            fig = plotar_grafico(
                dados['dias_list'],
                dados['pesos_list'],
                dados['fases_list'],
                dados['K'],
                dados['p_inicial'],
                dados['p_final'],
                dados['dias'],
                dados['data_inicial'],
                dados['cultivar_nome'],
                pesos_reais=dados.get('pesos_reais', None)
            )
            
            # Exibir o gráfico Plotly
            config = {'displayModeBar': False}
            st.plotly_chart(fig, use_container_width=True, config=config)
        except Exception as e:
            st.error(f"Erro ao plotar o gráfico: {e}")
            return
        
        # Criar datas usando timedelta e converter para strings
        datas_str = []
        for dia in dados['dias_list']:
            try:
                nova_data = dados['data_inicial'] + datetime.timedelta(days=dia-1)
                datas_str.append(nova_data.strftime('%d/%m/%Y'))
            except:
                datas_str.append(dados['data_inicial'].strftime('%d/%m/%Y'))
        
        # Criar DataFrame com coluna 'Real (g)' editável
        df = pd.DataFrame({
            'Dia': dados['dias_list'],
            'Data': datas_str,
            'Fase': dados['fases_list'],
            'Peso Previsto (g)': dados['pesos_list'],
            'Peso Real (g)': dados.get('pesos_reais', [None] * len(dados['dias_list']))
        })
        
        # Formatar dados
        df['Peso Previsto (g)'] = df['Peso Previsto (g)'].apply(lambda p: f"{p:.2f}")
        
        # Definir ordem das fases
        ordem_fases = CategoricalDtype(
            categories=["Lenta", "Acelerada", "Saturação"], 
            ordered=True
        )
        df['Fase'] = df['Fase'].astype(ordem_fases)
        
        # Container para título e botão de atualização - AGORA ACIMA DA TABELA
        col_titulo, col_botao = st.columns([4, 1])
        with col_titulo:
            st.subheader("Dados de Crescimento")
        with col_botao:
            # Botão de atualização
            if st.button("🔄 Atualizar", key="btn_atualizar", use_container_width=True):
                # Atualizar pesos reais na sessão com os valores temporários
                st.session_state.dados_grafico['pesos_reais'] = st.session_state.temp_pesos_reais.copy()
                # Forçar atualização do gráfico
                st.rerun()


        # Calcular altura necessária para exibir todas as linhas
        num_linhas = len(df)
        altura_linha = 22
        altura_total = (num_linhas * altura_linha) + 40

        # Exibir tabela editável diretamente (sem container de altura fixa)
        edited_df = st.data_editor(
            df,
            column_config={
                "Peso Real (g)": st.column_config.NumberColumn(
                    "Peso Real (g)",
                    help="Insira o peso real observado",
                    format="%.2f",
                    min_value=0.0,
                    step=0.1
                ),
                "Dia": st.column_config.Column(disabled=True),
                "Data": st.column_config.Column(disabled=True),
                "Fase": st.column_config.Column(disabled=True),
                "Peso Previsto (g)": st.column_config.Column(disabled=True)
            },
            use_container_width=True,
            hide_index=True,
            key="data_editor",
            num_rows="fixed",
            row_height = altura_linha,
            height = altura_total
        )
        
        # Armazenar alterações temporárias no session_state
        if 'temp_pesos_reais' not in st.session_state:
            st.session_state.temp_pesos_reais = dados.get('pesos_reais', [None] * len(dados['dias_list']))
        
        # Atualizar pesos reais temporários quando a tabela é editada
        if 'data_editor' in st.session_state:
            edited_data = st.session_state.data_editor['edited_rows']
            temp_pesos = st.session_state.temp_pesos_reais.copy()
            for idx, changes in edited_data.items():
                if 'Peso Real (g)' in changes:
                    temp_pesos[idx] = changes['Peso Real (g)']
            st.session_state.temp_pesos_reais = temp_pesos
        
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
