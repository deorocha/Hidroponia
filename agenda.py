import streamlit as st
from streamlit_calendar import calendar

# Configuração inicial da página
st.set_page_config(
    page_title="Agenda",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'About': None, 'Get help': None, 'Report a bug': None}
)

# Carregamento do CSS customizado externo
try:
    with open('./styles/style.css') as f:
        css_external = f.read()
    st.markdown(f"<style>{css_external}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Arquivo style.css não encontrado em ./styles/. Verifique o caminho.")
except Exception as e:
    st.error(f"Erro ao carregar style.css: {e}")

def main():
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>📅 Agenda</h2>",
            unsafe_allow_html=True)


        mode = st.sidebar.selectbox(
            "Tipo de calendário:",
            (
            "grade diária",                 # daygrid
            "grade temporal",               # timegrid
            "linha do tempo",               # timeline
            "grade diária de recursos",     # resource-daygrid
            "grade temporal de recursos",   # resource-timegrid
            "linha do tempo de recursos",   # resource-timeline
            "lista",                        # list
            "vários meses",                 # multimonth
            ),
        )

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

    events = [
        {"title": "Event 1", "color": "#FF6C6C", "start": "2023-07-03", "end": "2023-07-05", "resourceId": "a",},
        {"title": "Event 2", "color": "#FFBD45", "start": "2023-07-01", "end": "2023-07-10", "resourceId": "b",},
        {"title": "Event 3", "color": "#FF4B4B", "start": "2023-07-20", "end": "2023-07-20", "resourceId": "c",},
        {"title": "Event 4", "color": "#FF6C6C", "start": "2023-07-23", "end": "2023-07-25", "resourceId": "d",},
        {"title": "Event 5", "color": "#FFBD45", "start": "2023-07-29", "end": "2023-07-30", "resourceId": "e",},
        {"title": "Event 6", "color": "#FF4B4B", "start": "2023-07-28", "end": "2023-07-20", "resourceId": "f",},
        {"title": "Event 7", "color": "#FF4B4B", "start": "2023-07-01T08:30:00", "end": "2023-07-01T10:30:00", "resourceId": "a",},
        {"title": "Event 8", "color": "#3D9DF3", "start": "2023-07-01T07:30:00", "end": "2023-07-01T10:30:00", "resourceId": "b",},
        {"title": "Event 9", "color": "#3DD56D", "start": "2023-07-02T10:40:00", "end": "2023-07-02T12:30:00", "resourceId": "c",},
        {"title": "Event 10","color": "#FF4B4B", "start": "2023-07-15T08:30:00", "end": "2023-07-15T10:30:00", "resourceId": "d",},
        {"title": "Event 11","color": "#3DD56D", "start": "2023-07-15T07:30:00", "end": "2023-07-15T10:30:00", "resourceId": "e",},
        {"title": "Event 12","color": "#3D9DF3", "start": "2023-07-21T10:40:00", "end": "2023-07-21T12:30:00", "resourceId": "f",},
        {"title": "Event 13","color": "#FF4B4B", "start": "2023-07-17T08:30:00", "end": "2023-07-17T10:30:00", "resourceId": "a",},
        {"title": "Event 14","color": "#3D9DF3", "start": "2023-07-17T09:30:00", "end": "2023-07-17T11:30:00", "resourceId": "b",},
        {"title": "Event 15","color": "#3DD56D", "start": "2023-07-17T10:30:00", "end": "2023-07-17T12:30:00", "resourceId": "c",},
        {"title": "Event 16","color": "#FF6C6C", "start": "2023-07-17T13:30:00", "end": "2023-07-17T14:30:00", "resourceId": "d",},
        {"title": "Event 17","color": "#FFBD45", "start": "2023-07-17T15:30:00", "end": "2023-07-17T16:30:00", "resourceId": "e",},
    ]

    calendar_resources = [
        {"id": "a", "building": "Building A", "title": "Bancada 1"},
        {"id": "b", "building": "Building A", "title": "Bancada 2"},
        {"id": "c", "building": "Building B", "title": "Bancada 3"},
        {"id": "d", "building": "Building B", "title": "Bancada 4"},
        {"id": "e", "building": "Building C", "title": "Bancada 5"},
        {"id": "f", "building": "Building C", "title": "Bancada 6"},
    ]

    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "resources": calendar_resources,
        "selectable": "true",
        "locale": "pr-BR"
    }

    if "recursos" in mode:
        if mode == "grade diária de recursos":
            calendar_options = {
                **calendar_options,
                "initialDate": "2023-07-01",
                "initialView": "resourceDayGridDay",
                "resourceGroupField": "building",
            }
        elif mode == "inha do tempo de recursos":
            calendar_options = {
                **calendar_options,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
                },
                "initialDate": "2023-07-01",
                "initialView": "resourceTimelineDay",
                "resourceGroupField": "building",
            }
        elif mode == "grade temporal de recursos":
            calendar_options = {
                **calendar_options,
                "initialDate": "2023-07-01",
                "initialView": "resourceTimeGridDay",
                "resourceGroupField": "building",
            }
    else:
        if mode == "grade diária":
            calendar_options = {
                **calendar_options,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "dayGridDay,dayGridWeek,dayGridMonth",
                },
                "initialDate": "2023-07-01",
                "initialView": "dayGridMonth",
            }
        elif mode == "grade temporal":
            calendar_options = {
                **calendar_options,
                "initialView": "timeGridWeek",
            }
        elif mode == "linha do tempo":
            calendar_options = {
                **calendar_options,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "timelineDay,timelineWeek,timelineMonth",
                },
                "initialDate": "2023-07-01",
                "initialView": "timelineMonth",
            }
        elif mode == "lista":
            calendar_options = {
                **calendar_options,
                "initialDate": "2023-07-01",
                "initialView": "listMonth",
            }
        elif mode == "vários meses":
            calendar_options = {
                **calendar_options,
                "initialView": "multiMonthYear",
            }

    state = calendar(
        events=st.session_state.get("events", events),
        options=calendar_options,
        custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 500;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """,
        key=mode,
    )

    if state.get("eventsSet") is not None:
        st.session_state["events"] = state["eventsSet"]

    #st.write(state)
    #st.markdown("## API reference")
    #st.help(calendar)


if __name__ == "__main__":
    main()

