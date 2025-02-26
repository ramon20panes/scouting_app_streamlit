import streamlit as st
import pandas as pd
import numpy as np
from utils.auth import check_auth, logout
from common.pdf_export import export_to_pdf, download_pdf_button
import base64
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from utils.styles import load_all_styles
from utils.visualization import create_bumpy_chart 
import highlight_text
import os
from dotenv import load_dotenv
from utils.visualization import create_bumpy_chart, create_match_timeline
from data.api_handlers.football_data_api import load_teams_mapping, get_atletico_matches

# Configuración de la página
st.set_page_config(
    page_title="Atlético de Madrid 24/25",
    page_icon="⚽",
    layout="wide"
)

# Cargar estilos al principio del archivo
load_all_styles()

# Mostrar la sidebar explícitamente
st.markdown("""
    <style>
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"],
    div[data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
        position: relative !important;
        z-index: 1 !important;
        margin: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Añadir reducción de márgenes y espaciados
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
}
div[data-testid="stVerticalBlock"] > div {
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if not check_auth():
    st.switch_page("Aplic_Direcc_Deport.py")

# Título centrado
ESCUDO_PATH = Path("assets/escudos/atm.png")

# Título con escudo
col_title, col_logo = st.columns([5, 1])

with col_title:
    st.markdown("""
        <h2 style='text-align: left; margin-top: 10px; padding-top: 15px;'>
            Visualizaciones 24-25
        </h2>
    """, unsafe_allow_html=True)

with col_logo:
    # Añadir espacio antes de la imagen
    st.write("")  # Esto añade un pequeño espacio vertical
    st.image(ESCUDO_PATH, width=70)

# Reducir el espacio antes de los tabs
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    margin-bottom: -25px;
}
div[data-testid="stTabs"] {
    margin-top: -20px;
}
div[data-testid="stTabContent"] {
    padding-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Crear tabs para las diferentes visualizaciones
tab1, tab2, tab3 = st.tabs(["Clasificación LaLiga", "Timeline Partidos", "Expected Goals (xG)"])

# TAB 1 - Clasificación LaLiga
with tab1:
    # Cargar los datos
    @st.cache_data(ttl=3600)
    def load_liga_positions():
        csv_path = Path("data/FData/stats/liga_positions_24_25.csv")
        return pd.read_csv(csv_path)
    
    try:
        df = load_liga_positions()
    
        # Inicializar valores por defecto si es la primera vez
        if "highlight_teams" not in st.session_state:
            st.session_state.highlight_teams = ["Club Atlético de Madrid", "Real Madrid CF", "FC Barcelona"]

        # Seleccionar equipos a destacar con estado persistente
        highlight_teams = st.multiselect(
            "Equipos a destacar:",
            df["Equipo"].tolist(),
            default=st.session_state.highlight_teams
        )

        # Guardar la selección actual en session_state
        st.session_state.highlight_teams = highlight_teams
    
        # Crear y mostrar el gráfico
        fig, ax = create_bumpy_chart(df, highlight_teams)
        st.pyplot(fig)
    
    except Exception as e:
        st.error(f"Error al cargar o procesar los datos: {str(e)}")

# TAB 2 - Timeline Partidos
with tab2:
    st.subheader("Timeline de Partidos")
    
    @st.cache_data(ttl=3600)
    def load_atletico_matches():    
        # Cargar API key desde variables de entorno
        load_dotenv()
        api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    
        if not api_key:
            st.error("No se encontró la API Key para football-data.org. Verifica tu archivo .env")
            return None
    
        return get_atletico_matches(api_key)
    
    try:
        matches_df = load_atletico_matches()
        
        if matches_df is not None and not matches_df.empty:
            # Cargar el mapeo de equipos
            from data.api_handlers.football_data_api import load_teams_mapping
            team_mapping = load_teams_mapping()
            
            # Crear y mostrar el timeline
            from utils.visualization import create_match_timeline
            fig = create_match_timeline(matches_df, team_mapping)
            st.pyplot(fig)
            
            # Opcional: Mostrar tabla de datos
            with st.expander("Ver datos detallados"):
                st.dataframe(matches_df)
        else:
            st.warning("No se pudieron cargar los datos de partidos. Verifica tu conexión a la API.")
    
    except Exception as e:
        st.error(f"Error al cargar o procesar los datos: {str(e)}")
# TAB 3 - Expected Goals
with tab3:
    st.subheader("Análisis xG por Jornada")
    st.info("Esta visualización se implementará próximamente. Mostrará gráficos de xG (Expected Goals) para todas las jornadas, usando datos de Understat.")

# Obtener el nombre de la página actual
current_page = __file__.split('\\')[-1]

# Inicializar y actualizar el historial
if "page_history" not in st.session_state:
    st.session_state.page_history = []

# Actualizar historial solo si es una página nueva
if not st.session_state.page_history or st.session_state.page_history[-1] != current_page:
    st.session_state.page_history.append(current_page)

# Crear contenedor para botón de PDF y footer sin línea divisoria
st.markdown("---")
footer_container = st.container()

with footer_container:
        
    footer_cols = st.columns([1, 2, 1])
    
    # Columna izquierda - Botón PDF con texto incluido
    with footer_cols[0]:
        if st.button("📑 Exportar Informe PDF", key="generate_pdf"):
            pdf_data = {
                "Información General": "Visualizaciones Atlético de Madrid temporada 24/25",
                "Clasificación LaLiga": "Evolución de posiciones en la liga",
                "Timeline Partidos": "Calendario y resultados de partidos",
                "Análisis xG": "Análisis de Expected Goals por jornada"
            }

            # Generar PDF
            pdf_bytes = export_to_pdf(
                pdf_data, 
                filename=f"Gráfico_Atleti{datetime.now().strftime('%d%m%Y')}.pdf",
                title="Informe Atlético de Madrid - Visualizaciones 24/25"
            )
            
            # Mostrar botón de descarga
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.pdf_filename = f"Gráfico_Atleti{datetime.now().strftime('%d%m%Y')}.pdf"
            st.success("PDF generado correctamente")

        # Si hay un PDF generado, mostrar el botón de descarga
        if "pdf_bytes" in st.session_state and st.session_state.pdf_bytes:
            download_pdf_button(
                st.session_state.pdf_bytes,
                filename=st.session_state.pdf_filename
            )
    
    # Columna central - Espacio vacío
    with footer_cols[1]:
        pass
    
    # Columna derecha - Solo autor, ajustado verticalmente
    with footer_cols[2]:
        st.markdown("""
            <div style="text-align: right; margin-top: 5px;">
                <strong>Ramón González</strong><br>
                Mod8 MPAD
            </div>
        """, unsafe_allow_html=True)

with st.sidebar:
    # Espacio flexible
    st.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)
    
    # Botones al final
    container = st.container()
    with container:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back"):
                if len(st.session_state.page_history) > 1:
                    # Quitar página actual
                    st.session_state.page_history.pop()
                    # Ir a página anterior
                    previous_page = st.session_state.page_history[-1]
                    st.switch_page(f"pages/{previous_page}")
        with col2:
            if st.button("Exit"):
                logout()

    # CSS para posicionar los botones
    st.markdown("""
        <style>
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:last-child {
            position: fixed;
            bottom: 20px;
            padding: 1rem;
            width: inherit;
        }
        </style>
    """, unsafe_allow_html=True)