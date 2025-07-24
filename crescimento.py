"""
    Autor : André Luiz Rocha
    Data  : 05/06/2025 - 07:25
    L.U.  : 22/07/2025 - 19:54
    Programa: crescimento_2.py
    Função: Simulação de crescimento sigmoidal com Plotly
    Pendências:
        - Gravar os valores dos 'Pesos Reais' no BD;
        - 
"""

import streamlit as st
import sqlite3
import math
import numpy as np
import datetime
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Crescimento",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': None, 'Get help': None, 'Report a bug': None}
)

# HTML customizado
st.components.v1.html("""
<style>
    div[data-testid="stDataFrame"] div[data-testid="data-container"] > div,
    div[data-testid="stDataFrame"] > div,
    div[data-testid="stDataFrame"] {
        max-height: none !important;
        overflow-y: hidden !important;
    }
    div[data-testid="stDataFrame"] table {
        display: table !important;
        height: auto !important;
    }
    div[data-testid="stDataFrame"] th,  
    div[data-testid="stDataFrame"] td {
        padding: 2px 5px !important;
        height: 25px !important;
        line-height: 1.2 !important;
    }
    .block-container { padding-top: 0rem !important; }  /* REMOVIDO ESPAÇO ACIMA */
    h3 { margin-top: 0 !important; }
    section[data-testid="stSidebar"] { width: 300px !important; }
    .st-emotion-cache-1oe5cao { display: none !important; }
    .custom-sidebar-toggle {
        position: fixed;
        top: 5px;
        left: 10px;
        z-index: 1000;
        background: #f0f2f6;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px;
        cursor: pointer;
    }
    .stDateInput > div { flex-direction: row; }  /* FORMATO DATA */
    .stDateInput label { margin-right: 10px; }   /* FORMATO DATA */
    
    /* Estilos para os tooltips */
    .hovertext .fill {
        fill: #ECF5E7 !important;  /* Cor de fundo para previsão */
    }
    .hovertext-real .fill {
        fill: #FCE4D6 !important;  /* Cor de fundo para dados reais */
    }
    /* Estilo para alinhar botão com título */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
</style>
""")

# Constantes
DB_NAME = "./dados/hidroponia.db"
MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}
CORES_FASE = {"Lenta": "blue", "Acelerada": "green", "Saturação": "red"}
CORES_FASE_BG = {
    "Lenta": "#ECF4FA",
    "Acelerada": "#ECF5E7",
    "Saturação": "#FFF5D9"
}

# Funções núcleo corrigidas
def calcular_parametros(p_inicial, p_final, dias):
    """Calcula parâmetros da curva sigmoidal de forma robusta"""
    t0 = dias / 2.0
    K = p_final * 1.05
    tolerancia = 0.01
    max_iter = 1000
    
    for _ in range(max_iter):
        try:
            # Evitar divisão por zero e valores negativos
            if K <= p_inicial:
                K = p_inicial * 1.1
                continue
                
            # Calcular r com tratamento de exceções
            arg = (K / p_inicial) - 1
            if arg <= 0:
                K *= 1.1
                continue
                
            r = -math.log(arg) / (1 - t0)
            
            # Verificar convergência
            exp_term = math.exp(-r * (dias - t0))
            p_final_calculado = K / (1 + exp_term)
            
            if abs(p_final_calculado - p_final) < tolerancia:
                return K, r, t0
            
            # Ajustar K se necessário
            K *= p_final / p_final_calculado
            
        except (ValueError, ZeroDivisionError):
            K *= 1.1
            continue
    
    # Se não convergir, usar valores padrão
    return K, 0.1, t0

def classificar_fase(peso, K):
    """Classifica a fase de crescimento de forma eficiente"""
    ratio = peso / K
    return "Lenta" if ratio < 0.1 else "Saturação" if ratio > 0.9 else "Acelerada"

def gerar_dados_sigmoidal(p_inicial=5.0, p_final=260.0, dias=35):
    """Gera dados para curva de crescimento"""
    try:
        K, r, t0 = calcular_parametros(p_inicial, p_final, dias)
        dias_list = list(range(1, dias + 1))
        pesos_list = []
        
        for t in dias_list:
            try:
                exp_term = math.exp(-r * (t - t0))
                peso = K / (1 + exp_term)
                pesos_list.append(peso)
            except:
                pesos_list.append(0)
        
        fases_list = [classificar_fase(p, K) for p in pesos_list]
        return dias_list, pesos_list, fases_list, K, r
    except Exception as e:
        st.error(f"Erro no cálculo: {e}")
        return None, None, None, None, None

def gerar_datas(data_inicial, dias):
    """Gera lista de datas formatadas"""
    if isinstance(data_inicial, datetime.date):
        data_inicial = datetime.datetime.combine(data_inicial, datetime.time())
    
    datas = [data_inicial + datetime.timedelta(days=d-1) for d in range(1, dias+1)]
    datas_str = [d.strftime('%d/%m/%Y') for d in datas]
    dia_texto = [f"{d.day:02d}/{MESES_PT[d.month]}" for d in datas]
    return datas, datas_str, dia_texto

def plotar_grafico(dados, pesos_reais=None):
    """Gera o gráfico de crescimento otimizado com fundo colorido e linhas verticais"""
    # Desempacotar dados de forma segura
    try:
        dias_list, pesos_list, fases_list, K, p_inicial, p_final, dias, data_inicial, cultivar_nome = dados
    except Exception as e:
        st.error(f"Erro ao desempacotar dados: {e}")
        return None
    
    datas, datas_str, dia_texto = gerar_datas(data_inicial, dias)
    
    # DataFrame otimizado
    df = pd.DataFrame({
        'Data': datas,
        'DataStr': datas_str,
        'Dia': dias_list,
        'Peso (g)': pesos_list,
        'Fase': fases_list,
        'Dia_Texto': dia_texto
    })
    
    # Plot base com hover personalizado
    fig = px.scatter(
        df,
        x='Data',
        y='Peso (g)',
        color='Fase',
        color_discrete_map=CORES_FASE,
        custom_data=['DataStr', 'Peso (g)']  # Dados adicionais para o hover
    )
    
    # Formatação do hover e cor de fundo para previsão
    fig.update_traces(
        hovertemplate="<b>Data</b>: %{customdata[0]}<br><b>Peso</b>: %{customdata[1]:.2f} g<extra></extra>",
        hoverlabel=dict(bgcolor="#ECF5E7")  # Cor de fundo para previsão
    )
    
    # Linha de tendência
    fig.add_scatter(x=df['Data'], y=df['Peso (g)'], mode='lines', 
                   line=dict(color='green', width=2), name='Previsão',
                   hoverinfo='skip')  # Desativa hover na linha
    
    # Dados reais
    if pesos_reais and any(p is not None for p in pesos_reais):
        df_real = pd.DataFrame({
            'Data': datas,
            'Peso Real (g)': pesos_reais
        }).dropna()
        
        fig.add_scatter(
            x=df_real['Data'], 
            y=df_real['Peso Real (g)'], 
            mode='markers+lines',
            marker=dict(color='red', size=8, symbol='diamond'),
            line=dict(color='red', width=2), 
            name='Real',
            hovertemplate="<b>Data</b>: %{x|%d/%m/%Y}<br><b>Peso</b>: %{y:.2f} g<extra></extra>",
            hoverlabel=dict(bgcolor="#FCE4D6")  # Cor de fundo para dados reais
        )
    
    # Adicionar linhas verticais tracejadas cinza para cada dia
    for data in datas:
        fig.add_vline(
            x=data,
            line_width=1,
            line_dash="dot",
            line_color="gray",
            opacity=0.3
        )
    
    # Identificar limites das fases para fundo colorido
    fase_lenta = [i for i, fase in enumerate(fases_list) if fase == "Lenta"]
    fase_acelerada = [i for i, fase in enumerate(fases_list) if fase == "Acelerada"]
    fase_saturacao = [i for i, fase in enumerate(fases_list) if fase == "Saturação"]
    
    # Adicionar fundo colorido para cada fase com sobreposição corrigida
    if fase_lenta:
        # Correção: adicionar 1 dia para preencher completamente o intervalo
        fim_lenta = datas[fase_lenta[-1]] + datetime.timedelta(days=1)
        fig.add_vrect(
            x0=datas[0], 
            x1=fim_lenta,
            fillcolor=CORES_FASE_BG["Lenta"],
            opacity=0.5,
            layer="below",
            line_width=0,
        )
    
    if fase_acelerada:
        # Correção: adicionar 1 dia para preencher completamente o intervalo
        inicio_acelerada = datas[fase_acelerada[0]]
        fim_acelerada = datas[fase_acelerada[-1]] + datetime.timedelta(days=1)
        fig.add_vrect(
            x0=inicio_acelerada, 
            x1=fim_acelerada,
            fillcolor=CORES_FASE_BG["Acelerada"],
            opacity=0.5,
            layer="below",
            line_width=0,
        )
    
    if fase_saturacao:
        # Correção: adicionar 1 dia para preencher completamente o intervalo
        inicio_saturacao = datas[fase_saturacao[0]]
        fim_saturacao = datas[-1] + datetime.timedelta(days=1)
        fig.add_vrect(
            x0=inicio_saturacao, 
            x1=fim_saturacao,
            fillcolor=CORES_FASE_BG["Saturação"],
            opacity=0.5,
            layer="below",
            line_width=0,
        )
    
    # Elementos gráficos adicionais
    try:
        idx_meio = min(range(len(pesos_list)), key=lambda i: abs(pesos_list[i] - K/2))
        fig.add_vline(
            x=datas[idx_meio], 
            line_width=2, 
            line_dash="dot",
            line_color="purple", 
            annotation_text=f"Infleção ({dia_texto[idx_meio]})"
        )
    except:
        pass  # Não é crítico se falhar
    
    fig.add_hline(
        y=p_final, 
        line_width=2, 
        line_dash="dash", 
        line_color="darkorange", 
        opacity=0.7
    )
    
    # Configurações finais
    fig.update_layout(
        height=500,
        margin=dict(b=120, t=0, l=20, r=20),
        xaxis=dict(
            tickformat="%d/%b", 
            tickvals=datas,
            ticktext=dia_texto
        ),
        yaxis=dict(range=[0, max(pesos_list)*1.15]),
        # legend=dict(orientation='h', y=-0.15, x=0.5)
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.20,
            xanchor='center',
            x=0.5,
            traceorder='normal',
            itemwidth=50,
            title=dict(
                text='<b>Fases:</b>',  # "Fase:" integrada à legenda
                side='left'
            ),
            font=dict(size=12)
        )
    )
    
    return fig

@st.cache_data
def carregar_cultivares():
    """Carrega dados de cultivares com cache"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT clt_id, clt_nome, clt_periodo, clt_peso_colheita 
                FROM tbl_cultivares
            """)
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        return []

# Função principal corrigida
def main():
    # Inicialização de estado
    st.session_state.setdefault('mostrar_grafico', False)
    
    # Botão de toggle sidebar
    st.components.v1.html("""
    <div class="custom-sidebar-toggle" onclick="toggleSidebar()">
        <button id="sidebarBtn"><<</button>
    </div>
    <script>
        function toggleSidebar() {
            const sidebar = parent.document.querySelector('section[data-testid="stSidebar"]');
            const btn = parent.document.getElementById('sidebarBtn');
            sidebar.style.transform = sidebar.style.transform === 'translateX(-100%)' ? 
                'translateX(0)' : 'translateX(-100%)';
            btn.innerHTML = sidebar.style.transform === 'translateX(-100%)' ? '>>' : '<<';
        }
    </script>
    """, height=0)

    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='margin:0;'>📈 Crescimento</h2>", unsafe_allow_html=True)

        cultivares = carregar_cultivares()
        nomes_cultivares = [c[1] for c in cultivares]
        cultivar_info = {c[1]: (c[0], c[2], c[3]) for c in cultivares}
        
        cultivar_nome = st.selectbox('Cultivar:', nomes_cultivares)
        clt_id, periodo_default, peso_default = cultivar_info.get(cultivar_nome, (None, 35, 260.0))

        col1, col2 = st.columns([1, 1], vertical_alignment="center")
        with col1:
            st.markdown("##### Período (dias):")
        with col2:
            periodo_dias = st.number_input("", 0, 140, periodo_default)
        
        col1, col2 = st.columns([1, 1], vertical_alignment="center")
        with col1:
            st.markdown("##### Peso esperado (g):")
        with col2:
            peso_esperado = st.number_input("", 0.0, 1000.0, float(peso_default), step=1.0, format="%.2f")
        
        col1, col2 = st.columns([1, 1], vertical_alignment="center")
        with col1:
            st.markdown("##### Data do plantio:")
        with col2:
            data_plantio = st.date_input("", datetime.date.today(), format="DD/MM/YYYY")

        if st.button("📈 Mostrar Gráfico", use_container_width=True):
            try:
                dados_sigmoidal = gerar_dados_sigmoidal(5.0, peso_esperado, periodo_dias)
                if dados_sigmoidal[0] is not None:
                    st.session_state.dados_grafico = {
                        'dias_list': dados_sigmoidal[0],
                        'pesos_list': dados_sigmoidal[1],
                        'fases_list': dados_sigmoidal[2],
                        'K': dados_sigmoidal[3],
                        'p_inicial': 5.0,
                        'p_final': peso_esperado,
                        'dias': periodo_dias,
                        'data_inicial': data_plantio,
                        'cultivar_nome': cultivar_nome
                    }
                    st.session_state.mostrar_grafico = True
                    st.session_state.pesos_reais = [None] * len(dados_sigmoidal[0])
            except Exception as e:
                st.error(f"Erro: {e}")

        # Rodapé
        #st.markdown("<div style='flex-grow:1;'></div>", unsafe_allow_html=True)

        # Rodapé do sidebar com os botões
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()

    # Conteúdo principal
    if st.session_state.get('mostrar_grafico') and 'dados_grafico' in st.session_state:
        dados = st.session_state.dados_grafico
        
        # Verificar integridade dos dados
        required_keys = ['dias_list', 'pesos_list', 'fases_list', 'K', 'p_inicial', 
                         'p_final', 'dias', 'data_inicial', 'cultivar_nome']
        
        if not all(key in dados for key in required_keys):
            st.error("Estrutura de dados inválida para o gráfico")
            return
        
        # Container sem espaço superior
        with st.container():
            # Adicionar título compacto sem espaço superior
            st.markdown(f"""
            <h4 style='margin:0; padding:0; margin-top:0; padding-top:0;'>📈 Gráfico de crescimento: {dados['cultivar_nome']}</h4>
            """, unsafe_allow_html=True)
        
            # Criar tupla para a função plotar_grafico
            dados_tupla = (
                dados['dias_list'],
                dados['pesos_list'],
                dados['fases_list'],
                dados['K'],
                dados['p_inicial'],
                dados['p_final'],
                dados['dias'],
                dados['data_inicial'],
                dados['cultivar_nome']
            )
            
            fig = plotar_grafico(dados_tupla, st.session_state.get('pesos_reais'))
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.error("Não foi possível gerar o gráfico.")
            
            # Tabela de dados
            _, datas_str, _ = gerar_datas(dados['data_inicial'], dados['dias'])
            df = pd.DataFrame({
                'Dia': dados['dias_list'],
                'Data': datas_str,
                'Fase': dados['fases_list'],
                'Previsto (g)': [f"{p:.2f}" for p in dados['pesos_list']],
                'Real (g)': st.session_state.get('pesos_reais', [None] * len(dados['dias_list']))
            })

            # Container para título e botão de atualização
            col1, col_titulo, col_botao, col2 = st.columns([2, 4, 2, 2])
            with col_titulo:
                st.markdown("#### Dados de Crescimento")
            with col_botao:
                # Botão de atualização
                if st.button("🔄 Atualizar", key="btn_atualizar_grafico", use_container_width=True):
                    if 'data_editor' in st.session_state:
                        edited_data = st.session_state.data_editor['edited_rows']
                        novos_pesos = st.session_state.pesos_reais.copy()
                        for idx, val in edited_data.items():
                            if 'Real (g)' in val:
                                novos_pesos[idx] = val['Real (g)']
                        st.session_state.pesos_reais = novos_pesos
                        st.rerun()            

            # Calcular altura necessária para exibir todas as linhas
            num_linhas = len(df)
            altura_linha = 22
            altura_total = (num_linhas * altura_linha) + 40

            # Criar colunas para centralização (25% | 50% | 25%)
            col1, col2, col3 = st.columns([2, 6, 2])
            with col2:  # Coluna central (50% da largura)
                # Editor de dados
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Real (g)": st.column_config.NumberColumn(
                            format="%.2f", 
                            min_value=0.0, 
                            step=0.01
                        ),
                        "Dia": st.column_config.Column(disabled=True),
                        "Data": st.column_config.Column(disabled=True),
                        "Fase": st.column_config.Column(disabled=True),
                        "Previsto (g)": st.column_config.Column(disabled=True)
                    },
                    use_container_width=True,
                    hide_index=True,
                    key="data_editor",
                    num_rows="fixed",
                    row_height=altura_linha,
                    height=altura_total
                )
    else:
        # Container sem espaço superior
        with st.container():
            st.markdown("""
            <div style="text-align:center; padding:100px 0;">
                <h2>📈 Simulação de Crescimento</h2>
                <p>Selecione um cultivar e clique em "Mostrar Gráfico"</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
