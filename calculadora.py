"""
    Autor : André Luiz Rocha
    Data  : 01/06/2025 - 13:10
    L.U.  : 05/08/2025 - 21:21
    Programa: calculadora.py
    Função: Calcula as quantidades de nutrientes à partir dos parâmetros ambientais
    Pendências:
        - Cálculo da reposição de água para nutrientes acima do máximo;
        - Fazer um relatório resumido de procedimentos para o manejo,
          com opções de 'Imprimir' e 'Compartilhar';
        - 
"""

import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import joblib
import sqlite3
from PIL import Image
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode  # Removido JsCode

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
#CSS_PATH = "./styles/style.css"
JS_PATH = "./scripts/script_calc.js"
IMG_DIR = "./imagens"
DB_NAME = "./dados/hidroponia.db"

# Função para configurar grid com larguras específicas
def configure_grid(df, hidden_columns=None, table_type="main"):
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Configurações padrão
    gb.configure_grid_options(
        suppressMenuHide=True,
        suppressFieldDotNotation=True,
        domLayout='autoHeight'
    )
    
    # Definir proporções de flex para cada tipo de tabela
    flex_configs = {
        "main": {  # Tabela principal (Cultivar)
            "Nutriente": 30,
            "Previsto": 15,
            "Mínimo": 15,
            "Médio": 15,
            "Máximo": 15,
            "Status": 10
        },
        "below": {  # Nutrientes abaixo do mínimo
            "Nutriente": 30,
            "Previsto": 10,
            "Mínimo": 10,
            "Médio": 10,
            "Máximo": 10,
            "Dif. (%)": 15,
            "Repor (g)*": 15
        },
        "above": {  # Nutrientes acima do máximo
            "Nutriente": 30,
            "Previsto": 10,
            "Mínimo": 10,
            "Médio": 10,
            "Máximo": 10,
            "Dif. (%)": 15,
            "Repor (L)**": 15
        }
    }
    
    # Configurar todas as colunas
    for col in df.columns:
        # Configurações comuns
        col_opts = {
            'filter': False,
            'suppressMenu': True,
            'suppressMovable': True,
            'suppressSizeToFit': False,
            'autoSize': False,  # Desabilitar autoSize para usar flex
        }
        
        # Definir flex se estiver na configuração
        if col in flex_configs[table_type]:
            col_opts['flex'] = flex_configs[table_type][col]
            col_opts['minWidth'] = 100  # Largura mínima para evitar quebras
        
        # Alinhamento numérico para colunas de valores
        if col in ['Previsto', 'Mínimo', 'Médio', 'Máximo', 'Valor', 'Dif. (%)', 'Repor (g)*', 'Repor (L)**']:
            col_opts['type'] = ['numericColumn']
            col_opts['cellStyle'] = {'textAlign': 'right'}
        else:
            col_opts['cellStyle'] = {'textAlign': 'left'}
            
        gb.configure_column(col, **col_opts)
    
    # Ocultar colunas especificadas
    if hidden_columns:
        for col in hidden_columns:
            gb.configure_column(col, hide=True)
    
    # Aplicar estilo condicional usando classes CSS
    if 'Tipo' in df.columns:
        gb.configure_grid_options(
            rowClassRules={
                'macronutriente': 'data.Tipo === 1',
                'micronutriente': 'data.Tipo === 2'
            }
        )
    
    grid_options = gb.build()
    grid_options['headerHeight'] = 25
    grid_options['rowHeight'] = 25
    grid_options['defaultColDef'] = {
        'headerClass': 'header-class',
        'suppressMenu': True,
        'suppressFilterButton': True,
    }
    
    return grid_options

# Carregar recursos externos
def load_resources():
    """Carrega CSS, JS e imagens externos"""
    # CSS
    #if os.path.exists(CSS_PATH):
    #    with open(CSS_PATH) as f:
    #        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
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

    # CSS adicional para AgGrid
    aggrid_css = """
    <style>
        /* Estilo para cabeçalho */
        .header-class {
            background-color: #FFF5D9 !important;
            text-align: center !important;
            padding: 2px !important;  /* Reduzido */
        }
        
        /* Centralizar texto do cabeçalho */
        .ag-header-cell-label {
            justify-content: center !important;
            line-height: 20px !important;  /* Adicionado */
        }
        
        /* Remover completamente ícones de filtro e menu */
        .ag-header-cell-menu-button,
        .ag-header-icon.ag-header-cell-menu-button,
        .ag-icon.ag-icon-menu,
        .ag-icon.ag-icon-filter,
        .ag-header-cell-filter-button {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            visibility: hidden !important;
        }
        
        /* Remover espaço reservado para ícones */
        .ag-header-cell::after {
            content: none !important;
        }
        
        /* Centralizar conteúdo das células verticalmente */
        .ag-cell {
            display: flex !important;
            align-items: center !important;
            padding: 0 5px !important;  /* Reduzido */
            line-height: 22px !important; /* Reduzido */
        }
        
        /* Estilos condicionais para linhas */
        .ag-row.macronutriente {
            background-color: #ECF5E7 !important;
        }
        .ag-row.micronutriente {
            background-color: #ECF4FA !important;
        }
        
        /* Garantir que a tabela ocupe 100% da largura */
        .ag-theme-alpine {
            width: 100% !important;
        }
        
        /* Reduzir tamanho da fonte */
        .ag-theme-alpine .ag-cell,
        .ag-theme-alpine .ag-header-cell {
            font-size: 13px !important;  /* Adicionado */
        }
    </style>
    """
    st.markdown(aggrid_css, unsafe_allow_html=True)

# Funções de dados
@st.cache_data
def load_ia_model(path="./modelos/hidroponia_modelo.pkl"):
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
        
        cursor.execute("SELECT clt_id, clt_nome FROM tbl_cultivares WHERE clt_selecionado=1")
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
    """Carrega faixas do cultivar com cache da tbl_culturas_nutrientes"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Buscar valores mínimo, médio e máximo da nova tabela
        cursor.execute("""
            SELECT cnu_nutriente_id, cnu_valor_minimo, cnu_valor_medio, cnu_valor_maximo 
            FROM tbl_culturas_nutrientes 
            WHERE cnu_cultura_id = ?
        """, (cultivar_id,))
        # Retornar dicionário: nut_id -> (minimo, medio, maximo)
        return {nut_id: (minimo, medio, maximo) for nut_id, minimo, medio, maximo in cursor.fetchall()}
    except Exception as e:
        st.error(f"Erro ao carregar faixas: {e}")
        return {}

def render_sidebar():
    """Renderiza a barra lateral"""
    with st.sidebar:
        # Estilo específico para o selectbox na sidebar
        st.markdown("""
        <style>
            .sidebar-selectbox div[data-baseweb="select"] {
                width: 100% !important;
            }
            .sidebar-selectbox div[data-baseweb="select"] > div {
                width: 100% !important;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>🧮 Calculadora</h2>",
            unsafe_allow_html=True)

        # Container para o selectbox com classe específica
        with st.container():
            st.markdown('<div class="sidebar-selectbox">', unsafe_allow_html=True)
            cultivar_idx = st.selectbox(
                "Cultivar:",
                range(len(st.session_state.cultivares)),
                format_func=lambda i: st.session_state.cultivares[i][1],
                placeholder="Selecione um cultivar",
                index=None,
                key="cultivar"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Campos numéricos com rótulos na mesma linha
        def create_inline_input(label, min_val, max_val, default, step, key):
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                st.markdown(f"<div style='line-height: 2.8; font-size: 12px;'>{label}</div>", unsafe_allow_html=True)
            with col2:
                return st.number_input("", min_val, max_val, default, step, key=key, label_visibility="collapsed")

        temp = create_inline_input("Temperatura (°C)", 0.0, 50.0, 25.0, 0.1, "temp")
        ph = create_inline_input("Potencial (pH)", 0.0, 14.0, 5.5, 0.1, "ph")
        ec = create_inline_input("Condutividade (EC)", 0.0, 10.0, 1.0, 0.01, "ec")
        o2 = create_inline_input("Oxigênio Dissolvido (O₂)", 0.0, 20.0, 4.0, 0.1, "o2")
        volume = create_inline_input("Volume do tanque (L)", 1, 100000, 1000, 10, "volume")

        return {
            'params': {
                'Temp': temp,
                'pH': ph,
                'EC': ec,
                'O2': o2,
            },
            'cultivar_idx': cultivar_idx,
            'volume': volume
        }

def render_main_results(prediction, cultivar_idx, volume):
    """Renderiza os resultados principais da previsão usando AgGrid"""
    # Mapear símbolo para tipo (1: macronutriente, 2: micronutriente)
    tipo_por_simbolo = {}
    for simbolo in st.session_state.macronutrientes:
        tipo_por_simbolo[simbolo] = 1
    for simbolo in st.session_state.micronutrientes:
        tipo_por_simbolo[simbolo] = 2
    
    nutriente_names = [f"{nome} ({simbolo})" for nome, simbolo in 
                      zip(st.session_state.nomes_completos, st.session_state.colunas_saida)]
    
    if cultivar_idx is None:
        # Construir DataFrame sem faixas
        data = {
            "Nutriente": nutriente_names,
            "Valor Previsto": [f"{v:.3f}" for v in prediction],
            "Tipo": [tipo_por_simbolo.get(simbolo, 0) for simbolo in st.session_state.colunas_saida]
        }
        df = pd.DataFrame(data)
        
        # Configurar grid
        hidden_columns = ['Tipo']
        grid_options = configure_grid(df, hidden_columns=hidden_columns, table_type="main")
        
        # Exibir
        AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=False,
            height=min(400, (len(df) + 1) * 30 + 40), # Alterado
            theme='alpine'
        )
        return None, None
    
    cultivar_id = st.session_state.cultivares[cultivar_idx][0]
    cultivar_name = st.session_state.cultivares[cultivar_idx][1]
    # st.subheader(f"Cultivar: :red[{st.session_state.cultivares[cultivar_idx][1]}]")
    st.markdown(
        f"<h3 style='margin-top:0; margin-bottom:0; padding-top:0; padding-bottom:0;'>"
        f"Cultivar: <span style='color:red'>{cultivar_name}</span></h3>",
        unsafe_allow_html=True
    )
 
    faixas = load_cultivar_ranges(cultivar_id)
    
    if not faixas:
        st.warning("⚠️ Nenhuma faixa definida para este cultivar.")
        # Construir DataFrame sem faixas
        data = {
            "Nutriente": nutriente_names,
            "Valor Previsto": [f"{v:.3f}" for v in prediction],
            "Tipo": [tipo_por_simbolo.get(simbolo, 0) for simbolo in st.session_state.colunas_saida]
        }
        df = pd.DataFrame(data)
        hidden_columns = ['Tipo']
        grid_options = configure_grid(df, hidden_columns=hidden_columns, table_type="main")
        AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=False,
            height=min(400, (len(df) + 1) * 30 + 40),
            theme='alpine'
        )
        return None, None
    
    resultados, reposicao_abaixo, reposicao_acima = [], [], []
    
    for i, nut_id in enumerate(st.session_state.ids_nutrientes):
        valor = prediction[i]
        valor_fmt = f"{valor:.3f}"
        status, min_fmt, med_fmt, max_fmt = "", "N/A", "N/A", "N/A"
        
        # Obter símbolo e tipo
        simbolo = st.session_state.colunas_saida[i]
        tipo = tipo_por_simbolo.get(simbolo, 0)
        
        if nut_id in faixas:
            minimo, medio, maximo = faixas[nut_id]
            min_fmt, med_fmt, max_fmt = f"{minimo:.3f}", f"{medio:.3f}", f"{maximo:.3f}"
            
            if valor < minimo:
                status = "🔻"
                reposicao_g = ((medio - valor) * volume) / 1000  # Meta é o valor médio
                dif_perc = ((medio - valor) / valor) * 100
                reposicao_abaixo.append({
                    "Nutriente": f"{st.session_state.nomes_completos[i]} ({simbolo})",
                    "Previsto": valor_fmt,
                    "Mínimo": min_fmt,
                    "Médio": med_fmt,
                    "Máximo": max_fmt,
                    "Dif. (%)": f"{dif_perc:.2f}",
                    "Repor (g)*": f"{reposicao_g:.2f}",
                    "Tipo": tipo
                })
            elif valor > maximo:
                status = "🔼"
                reposicao_l = (valor - maximo) * volume / maximo
                dif_perc = ((valor - maximo) / maximo) * 100
                reposicao_acima.append({
                    "Nutriente": f"{st.session_state.nomes_completos[i]} ({simbolo})",
                    "Previsto": valor_fmt,
                    "Mínimo": min_fmt,
                    "Médio": med_fmt,
                    "Máximo": max_fmt,
                    "Dif. (%)": f"{dif_perc:.2f}",
                    "Repor (L)**": f"{reposicao_l:.2f}",
                    "Tipo": tipo
                })
            else:
                status = "✅"
                
        resultados.append({
            "Nutriente": nutriente_names[i],
            "Previsto": valor_fmt,
            "Mínimo": min_fmt,
            "Médio": med_fmt,
            "Máximo": max_fmt,
            "Status": status,
            "Tipo": tipo
        })
    
    # Construir DataFrame para resultados principais
    df_resultados = pd.DataFrame(resultados)
    hidden_columns = ['Tipo']
    grid_options = configure_grid(df_resultados, hidden_columns=hidden_columns, table_type="main")
    AgGrid(
        df_resultados,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        fit_columns_on_grid_load=False,
        height=min(400, (len(df_resultados) + 1) * 25 + 30),
        theme='alpine'
    )
    st.success("✅ Previsão realizada com sucesso!")
    return reposicao_abaixo, reposicao_acima

def render_reposicao_section(title, icon, data, caption):
    """Renderiza uma seção de reposição usando AgGrid"""
    with st.container():
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            if icon:
                st.image(icon, width=30)
        with col2:
            # st.subheader(title)
            st.markdown("##### " + title)
        
        if data:
            df = pd.DataFrame(data)
            # Configurar grid
            hidden_columns = ['Tipo']
            
            # Determinar o tipo de tabela baseado no título
            table_type = "below" if "abaixo" in title else "above"
            grid_options = configure_grid(df, hidden_columns=hidden_columns, table_type=table_type)
            
            # Exibir
            AgGrid(
                df,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.NO_UPDATE,
                fit_columns_on_grid_load=False,
                height=min(300, (len(df) + 1) * 25 + 30),
                theme='alpine'
            )
            st.caption(caption)

def main():
    load_resources()
    
    # CORREÇÃO 1: Verificar diretamente o modelo ao invés de db_data
    if "model" not in st.session_state:
        st.session_state.db_data = load_db_data()
        st.session_state.update(st.session_state.db_data)
        st.session_state.model = load_ia_model()
    
    sidebar_data = render_sidebar()
    
    if st.sidebar.button("🔍 Realizar Previsão", use_container_width=True):
        try:
            # Inicializar variáveis para evitar erros
            reposicao_abaixo = []
            reposicao_acima = []
            
            input_data = pd.DataFrame([list(sidebar_data['params'].values())], 
                                     columns=['Temp', 'pH', 'EC', 'O2'])
            prediction = st.session_state.model.predict(input_data)[0]
            
            # Receber resultados e garantir que sejam listas
            repos_abaixo, repos_acima = render_main_results(
                prediction, 
                sidebar_data['cultivar_idx'], 
                sidebar_data['volume']
            )
            reposicao_abaixo = repos_abaixo or []
            reposicao_acima = repos_acima or []
            
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
                
            # CSS embutido diretamente no componente
            box_component = f"""
            <style>
                .custom-box {{
                    width: 800px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    margin: 20px auto;
                    overflow: hidden;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}

                .custom-title-bar {{
                    height: 40px;
                    background-color: #e8f9ee;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 0 15px;
                    color: black;
                }}

                .custom-title {{
                    font-weight: 600;
                    font-size: 16px;
                }}

                .custom-icons {{
                    display: flex;
                    gap: 15px;
                }}

                .custom-icon {{
                    cursor: pointer;
                    font-size: 18px;
                    transition: all 0.3s;
                }}

                .custom-icon:hover {{
                    transform: scale(1.1);
                    color: #3498db;
                }}

                .custom-content {{
                    padding: 20px;
                    color: #333;
                }}
                
                .reposicao-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    font-size: 14px;
                }}
                
                .reposicao-table th {{
                    background-color: #f2f2f2;
                    padding: 8px;
                    border: 1px solid #ddd;
                }}
                
                .reposicao-table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                }}
                
                .reposicao-table tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                
                /* ALTERAÇÃO PRINCIPAL: Alinhamento de colunas numéricas */
                .reposicao-table th:nth-child(n+2),
                .reposicao-table td:nth-child(n+2) {{
                    text-align: right;
                    font-family: monospace;
                }}
                
                .reposicao-table th:first-child,
                .reposicao-table td:first-child {{
                    text-align: left;
                }}
            </style>

            <div class="custom-box">
                <div class="custom-title-bar">
                    <div class="custom-title">📊 Relatório de Manejo - Reposições</div>
                    <div class="custom-icons">
                        <span class="custom-icon" title="Imprimir" onclick="alert('Função de impressão acionada!')">🖨️</span>
                        <span class="custom-icon" title="Compartilhar" onclick="alert('Função de compartilhamento acionada!')">📤</span>
                    </div>
                </div>
                <div class="custom-content">
                    <h4>Nutrientes abaixo do mínimo:</h4>
                    {
                        '<table class="reposicao-table">'
                        '<tr><th>Nutriente</th><th>Previsto</th><th>Mínimo</th><th>Médio</th><th>Máximo</th><th>Dif. (%)</th><th>Repor (g)*</th></tr>' + 
                        ''.join([f'<tr><td>{item["Nutriente"]}</td><td>{item["Previsto"]}</td><td>{item["Mínimo"]}</td><td>{item["Médio"]}</td><td>{item["Máximo"]}</td><td>{item["Dif. (%)"]}</td><td>{item["Repor (g)*"]}</td></tr>' 
                                for item in reposicao_abaixo]) + 
                        '</table>' 
                        if reposicao_abaixo 
                        else '<p>Nenhum nutriente abaixo do mínimo</p>'
                    }
                    <h4>Nutrientes acima do máximo:</h4>
                    {
                        '<table class="reposicao-table">'
                        '<tr><th>Nutriente</th><th>Previsto</th><th>Mínimo</th><th>Médio</th><th>Máximo</th><th>Dif. (%)</th><th>Repor (L)**</th></tr>' + 
                        ''.join([f'<tr><td>{item["Nutriente"]}</td><td>{item["Previsto"]}</td><td>{item["Mínimo"]}</td><td>{item["Médio"]}</td><td>{item["Máximo"]}</td><td>{item["Dif. (%)"]}</td><td>{item["Repor (L)**"]}</td></tr>' 
                                for item in reposicao_acima]) + 
                        '</table>' 
                        if reposicao_acima 
                        else '<p>Nenhum nutriente acima do máximo</p>'
                    }
                </div>
            </div>
            """

            # Renderização
            html(box_component, height=340 + (len(reposicao_abaixo) * 30) + (len(reposicao_acima) * 30))
                
        except Exception as e:
            st.error(f"Erro na previsão: {str(e)}")

    with st.sidebar:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", key="btn_back_calculadora", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_calculadora", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

if __name__ == "__main__":
    main()
