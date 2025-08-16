"""
    Autor : André Luiz Rocha
    Data  : 05/06/2025 - 07:25
    L.U.  : 05/08/2025 - 21:22
    Programa: cresc.py
    Função: Simulação de crescimento sigmoidal com Plotly
    Pendências:
        - 
"""

import streamlit as st
import sqlite3
import math
from datetime import datetime, timedelta, date
import plotly.express as px
import pandas as pd
import numpy as np

# Configuração inicial da página
st.set_page_config(
    page_title="Crescimento",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': None,
        'Get help': None,
        'Report a bug': None
    }
)

DB_NAME = "./dados/hidroponia.db"

# Inicializa o estado da sessão
if 'show_graph' not in st.session_state:
    st.session_state.show_graph = False

if 'registros_df' not in st.session_state:
    st.session_state.registros_df = pd.DataFrame()

def carregar_bancadas():
    """Carrega a lista de bancadas do banco de dados"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT bcd_id, bcd_nome FROM tbl_bancadas ORDER BY bcd_nome")
        bancadas = cursor.fetchall()
        conn.close()
        
        return [(b[0], b[1]) for b in bancadas]
    except Exception as e:
        st.error(f"Erro ao carregar bancadas: {e}")
        return []

def carregar_cultivares():
    """Carrega a lista de cultivares do banco de dados"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT clt_id, clt_nome, clt_periodo, clt_peso_colheita FROM tbl_cultivares WHERE clt_selecionado=1 ORDER BY clt_nome")
        cultivares = cursor.fetchall()
        conn.close()
        
        return [(c[0], c[1], c[2], c[3]) for c in cultivares]  # (id, nome, periodo, peso)
    except Exception as e:
        st.error(f"Erro ao carregar cultivares: {e}")
        return []

def verificar_crescimento(bancada_id, cultivar_id, data_plantio):
    """Verifica se existem registros na tabela tbl_crescimento"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cre_id, cre_data, cre_fase_id, cre_peso_esperado, cre_peso_real
            FROM tbl_crescimento
            WHERE cre_bancada_id = ? AND cre_cultivar_id = ? AND cre_data_plantio = ?
            ORDER BY cre_data
        """, (bancada_id, cultivar_id, data_plantio))
        registros = cursor.fetchall()
        conn.close()
        
        # Mapeamento de fases
        fases = {
            1: "Lenta",
            2: "Acelerada",
            3: "Saturação"
        }
        
        # Transforma em lista de dicionários para o data_editor
        if registros:
            processed_records = []
            for idx, registro in enumerate(registros):
                # Convert string dates to date objects if needed
                record_date = registro[1]
                if isinstance(record_date, str):
                    try:
                        record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
                    except ValueError:
                        record_date = date.today()  # fallback to today if parsing fails
                
                processed_records.append({
                    "Dia": idx + 1,
                    "Data": record_date,
                    "Fase": fases.get(registro[2], registro[2]),  # Mostra o label da fase
                    "Peso previsto (g)": round(float(registro[3]), 2) if registro[3] is not None else 0.0,
                    "Peso real (g)": round(float(registro[4]), 2) if registro[4] is not None else None,
                    "_fase_id": registro[2]  # Mantém o ID para atualização
                })
            return processed_records
        return None
    except Exception as e:
        st.error(f"Erro ao verificar registros: {e}")
        return None

def verificar_cultivar(cultivar_id):
    """Obtém período e peso esperado do cultivar"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT clt_periodo, clt_peso_colheita FROM tbl_cultivares WHERE clt_id = ?", (cultivar_id,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado if resultado else (0, 0.0)
    except Exception as e:
        st.error(f"Erro ao obter informações do cultivar: {e}")
        return (0, 0.0)

def criar_grafico(registros_df, cultivar_nome="Desconhecido"):
    """Cria um gráfico de crescimento com os dados reais"""
    if registros_df.empty:
        return None
        
    # Processar o DataFrame para o gráfico
    df = registros_df.copy()
    df["Data"] = pd.to_datetime(df["Data"])

    # Criar o gráfico com ambas as linhas
    fig = px.line(
        df,
        x="Data",
        y=["Peso previsto (g)", "Peso real (g)"],
        color_discrete_sequence=["#81C784", "#FF5252"],
        labels={"value": "Peso (g)", "variable": ""},
    )
    
    # Mapear os nomes das colunas para os nomes desejados na legenda
    new_names = {'Peso previsto (g)':'Peso Previsto', 'Peso real (g)':'Peso Real'}
    fig.for_each_trace(lambda t: t.update(name = new_names[t.name]))
    
    # Configurar tooltips individuais para cada linha
    fig.update_traces(
        selector={"name": "Peso Previsto"},
        hovertemplate="<b>Data</b>: %{x|%d/%m/%Y}<br><b>Peso previsto</b>: %{y:.2f} g<extra></extra>",
        hoverlabel=dict(bgcolor="#ECF5E7", font_size=12)
    )
    
    fig.update_traces(
        selector={"name": "Peso Real"},
        hovertemplate="<b>Data</b>: %{x|%d/%m/%Y}<br><b>Peso real</b>: %{y:.2f} g<extra></extra>",
        hoverlabel=dict(bgcolor="#FCE4D6", font_size=12)
    )

    # Adicionar pontos para ambas as linhas
    for i, row in df.iterrows():
        # Pontos para Peso Real
        fig.add_scatter(
            x=[row["Data"]],
            y=[row["Peso real (g)"]],
            mode='markers',
            marker=dict(color="#FF5252", size=8),
            showlegend=False,
            hoverinfo="skip"
        )
        
        # Pontos para Peso Previsto
        fig.add_scatter(
            x=[row["Data"]],
            y=[row["Peso previsto (g)"]],
            mode='markers',
            marker=dict(color="#81C784", size=8),
            showlegend=False,
            hoverinfo="skip"
        )

    # Configuração do eixo X
    meses_pt = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
    ticktext = [f"{d.day}/{meses_pt[d.month]}" for d in df["Data"]]

    # Personalização do layout
    fig.update_layout(
        height=600,
        xaxis=dict(
            tickvals=df["Data"],
            ticktext=ticktext,
            tickangle=90,
            tickfont=dict(size=12),
            title=dict(standoff=10)
        ),
        yaxis=dict(title="Peso (g)"),
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        hovermode="closest",
        spikedistance=-1,
        hoverdistance=-1,
        margin=dict(t=40, b=40, l=40, r=40),
        title=dict(
            text=f"Evolução do Crescimento: {cultivar_nome}",
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(
                size=20,
                family="Arial",
                color="#333333",
                weight="normal"
            )
        )
    )

    phase_intervals = []
    current_phase = None
    start_date = None
    
    for i, row in df.iterrows():
        if row["Fase"] != current_phase:
            if current_phase is not None:
                phase_intervals.append({
                    "phase": current_phase,
                    "start": start_date,
                    "end": row["Data"]
                })
            current_phase = row["Fase"]
            start_date = row["Data"]
    
    if current_phase is not None:
        phase_intervals.append({
            "phase": current_phase,
            "start": start_date,
            "end": df.iloc[-1]["Data"]
        })

    for interval in phase_intervals:
        fig.add_vrect(
            x0=interval["start"],
            x1=interval["end"],
            fillcolor={
                "Lenta": "#ECF4FA",
                "Acelerada": "#ECF5E7",
                "Saturação": "#FFF5D9"
            }[interval["phase"]],
            opacity=0.7,
            layer="below",
            line_width=0,
            annotation_text=interval["phase"],
            annotation_position="top left"
        )

    for date in df["Data"]:
        fig.add_vline(
            x=date,
            line_dash="dot",
            line_color="gray",
            line_width=1,
            opacity=0.3
        )

    return fig

def calcular_parametros(p_inicial, p_final, dias):
    """Calcula parâmetros da curva sigmoidal de forma robusta"""
    t0 = dias / 2.0
    K = p_final * 1.05
    tolerancia = 0.01
    max_iter = 1000
    
    for _ in range(max_iter):
        try:
            if K <= p_inicial:
                K = p_inicial * 1.1
                continue
                
            arg = (K / p_inicial) - 1
            if arg <= 0:
                K *= 1.1
                continue
                
            r = -math.log(arg) / (1 - t0)
            
            exp_term = math.exp(-r * (dias - t0))
            p_final_calculado = K / (1 + exp_term)
            
            if abs(p_final_calculado - p_final) < tolerancia:
                return K, r, t0
            
            K *= p_final / p_final_calculado
            
        except (ValueError, ZeroDivisionError):
            K *= 1.1
            continue
    
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

def gerar_registros_df(dados_sigmoidal, data_plantio):
    dias = dados_sigmoidal[0]
    pesos_previstos = dados_sigmoidal[1]
    fases = dados_sigmoidal[2]
    
    fase_para_id = {
        "Lenta": 1,
        "Acelerada": 2,
        "Saturação": 3
    }
    
    registros = []
    
    for i in range(len(dias)):
        dia = dias[i]
        data = data_plantio + timedelta(days=dia-1)
        fase = fases[i]
        peso_previsto = round(pesos_previstos[i], 2)
        
        registros.append({
            "Dia": dia,
            "Data": data,
            "Fase": fase,
            "Peso previsto (g)": peso_previsto,
            "Peso real (g)": None,
            "_fase_id": fase_para_id[fase],
        })
    
    df = pd.DataFrame(registros)
    df = df.astype({
        "Dia": "int64",
        "Data": "datetime64[ns]",
        "Fase": "object",
        "Peso previsto (g)": "float64",
        "Peso real (g)": "float64",
        "_fase_id": "int64",
    })

    return df

def get_periodo(periodo, chave):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("Período (dias):")
    with col2:
        periodo_input = st.number_input(
            "",
            min_value=1,
            value=periodo,
            key=chave,
            label_visibility="collapsed"
        )
    return periodo_input

def get_peso(peso, chave):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("Peso esperado (g):")
    with col2:
        peso_input = st.number_input(
            "",
            min_value=0.0,
            value=float(peso),
            step=0.1,
            key=chave,
            label_visibility="collapsed"
        )
    return peso_input

def main():
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>📈 Crescimento</h2>",
                    unsafe_allow_html=True)
        
        bancada_id = None
        bancadas = carregar_bancadas()
        if bancadas:
            bancada_selecionada = st.selectbox(
                "Bancada:",
                options=bancadas,
                format_func=lambda x: x[1],
                key="select_bancada"
            )
            if bancada_selecionada:
                bancada_id = bancada_selecionada[0]
        else:
            st.warning("Nenhuma bancada cadastrada no sistema.")

        cultivar_id = None
        cultivares = carregar_cultivares()
        if cultivares:
            cultivar_selecionado = st.selectbox(
                "Cultivar:",
                options=cultivares,
                format_func=lambda x: x[1],
                key="select_cultivar"
            )
            if cultivar_selecionado:
                cultivar_id = cultivar_selecionado[0]
                periodo_default = cultivar_selecionado[2]
                peso_default = cultivar_selecionado[3]
        else:
            st.warning("Nenhum cultivar cadastrado no sistema.")

        col1, col2 = st.columns([4, 3], vertical_alignment="center")
        with col1:
            st.markdown("Data do plantio:")
        with col2:
            data_plantio = st.date_input(
                "",
                value=datetime.now().date(),
                key="data_plantio",
                label_visibility="collapsed",
                format="DD/MM/YYYY"
            )

        periodo_default, peso_default = verificar_cultivar(cultivar_id)
        periodo_input = get_periodo(periodo_default, "periodo_dias")
        peso_input = get_peso(peso_default, "peso_esperado")

        #if bancada_id and cultivar_id and data_plantio:
        #    registros_existentes = verificar_crescimento(bancada_id, cultivar_id, data_plantio)
        #    if registros_existentes:
        #        # periodo, peso_esperado = verificar_cultivar(cultivar_id)
        #        periodo_input = get_periodo(periodo_default, "periodo_dias")
        #        peso_input = get_peso(peso_default, "peso_esperado")
        #    else:
        #        periodo_input = get_periodo(periodo_default, "periodo_dias_novo")
        #        peso_input = get_peso(peso_default, "peso_esperado_novo")
    
    if bancada_id and cultivar_id and data_plantio and periodo_input is not None and peso_input is not None:
        registros_existentes = verificar_crescimento(bancada_id, cultivar_id, data_plantio)
        if registros_existentes:
            st.sidebar.write(f"{len(registros_existentes)} registros.")
        
        mostrar_grafico = st.sidebar.button("📈 Mostrar Gráfico", use_container_width=True)
      
        current_config = (bancada_id, cultivar_id, data_plantio, periodo_input, peso_input)

        if mostrar_grafico:
            st.session_state.show_graph = True
            registros_existentes = verificar_crescimento(bancada_id, cultivar_id, data_plantio)
            if registros_existentes:
                st.session_state.registros_df = pd.DataFrame(registros_existentes)
            else:
                dados_sigmoidal = gerar_dados_sigmoidal(5.0, peso_input, periodo_input)
                st.session_state.registros_df = gerar_registros_df(dados_sigmoidal, data_plantio)
            st.session_state.last_config = current_config
        elif st.session_state.get('last_config') != current_config:
            st.session_state.show_graph = False

        if st.session_state.show_graph and not st.session_state.registros_df.empty:
            cultivar_nome = next((c[1] for c in cultivares if c[0] == cultivar_id), "Desconhecido")

            fig = criar_grafico(st.session_state.registros_df, cultivar_nome=cultivar_nome)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3 = st.columns([2, 6, 2])
            with col2:
                st.markdown("Registros de Crescimento")
                editor_key = f"data_editor_{bancada_id}_{cultivar_id}_{data_plantio}"
                
                # Criar uma cópia do DataFrame para o editor, excluindo a coluna interna
                display_df = st.session_state.registros_df.drop(columns=['_fase_id'])
                
                edited_df = st.data_editor(
                    display_df,
                    column_config={
                        "Dia": st.column_config.NumberColumn("Dia", disabled=True),
                        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY", disabled=True),
                        "Fase": st.column_config.TextColumn("Fase", disabled=True),
                        "Peso previsto (g)": st.column_config.NumberColumn("Peso previsto (g)", format="%.2f", disabled=True),
                        "Peso real (g)": st.column_config.NumberColumn("Peso real (g)", format="%.2f")
                    },
                    hide_index=True,
                    height=(len(st.session_state.registros_df) * 35) + 40,
                    key=editor_key
                )
                
                # Atualizar diretamente a coluna do DataFrame da session_state
                st.session_state.registros_df['Peso real (g)'] = edited_df['Peso real (g)']
        elif st.session_state.show_graph and st.session_state.registros_df.empty:
             st.warning("Não há registros para a bancada e cultivar selecionados.")
        else:
            st.info("Aguardando carregamento de registros...")


    if st.button("Salvar Alterações", key="btn_salvar"):
        if 'registros_df' in st.session_state and not st.session_state.registros_df.empty:
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                
                for index, row in st.session_state.registros_df.iterrows():
                    # Verifica se o registro já existe
                    cursor.execute("""
                        SELECT cre_id FROM tbl_crescimento
                        WHERE cre_bancada_id = ?
                        AND cre_cultivar_id = ?
                        AND cre_data_plantio = ?
                        AND cre_data = ?
                    """, (
                        bancada_id,
                        cultivar_id,
                        data_plantio.strftime('%Y-%m-%d'),
                        row["Data"].strftime('%Y-%m-%d')
                    ))
                    existing_record = cursor.fetchone()
                    
                    if existing_record:
                        # Atualiza o registro existente
                        cursor.execute("""
                            UPDATE tbl_crescimento
                            SET cre_peso_real = ?
                            WHERE cre_id = ?
                        """, (
                            round(row["Peso real (g)"], 2),
                            existing_record[0]
                        ))
                    else:
                        # Insere novo registro
                        cursor.execute("""
                            INSERT INTO tbl_crescimento (
                                cre_bancada_id, cre_cultivar_id, cre_data_plantio, cre_data,
                                cre_fase_id, cre_peso_esperado, cre_peso_real
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            bancada_id,
                            cultivar_id,
                            data_plantio.strftime('%Y-%m-%d'),
                            row["Data"].strftime('%Y-%m-%d'),
                            row["_fase_id"],
                            round(row["Peso previsto (g)"], 2),
                            round(row["Peso real (g)"], 2)
                        ))
                
                conn.commit()
                conn.close()
                st.success("Alterações salvas com sucesso!")
                
            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")
        else:
            st.warning("Não há dados para salvar. Por favor, carregue os registros primeiro.")

    # st.sidebar.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
    # st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns([1, 1])
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

    with st.sidebar:
        with st.expander("Fases do desenvolvimento:"):
            st.markdown('''
                <div style="font-size: 12px">
                    1. Germinação: A semente absorve água e começa a desenvolver a radícula (raiz) e o epicótilo (caule).<br>
                    2. Crescimento Vegetativo: A planta desenvolve ativamente raízes, caules e folhas...<br>
                    3. Fase Juvenil: A planta continua crescendo, com desenvolvimento das partes vegetativas, preparando-se para a floração.<br>
                    4. Fase Adulta/Floração: A planta atinge a maturidade sexual, desenvolvendo flores que produzirão sementes para a reprodução.<br>
                    5. Frutificação e Maturação: As flores são polinizadas e desenvolvem frutos, que contêm as sementes.<br>
                    6. Senescência: A planta envelhece e pode perder folhas e flores, com diminuição da produção de energia.
                </div>
            ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
