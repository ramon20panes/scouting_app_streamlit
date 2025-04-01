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
import highlight_text
from highlight_text import fig_text

import os
from dotenv import load_dotenv

from utils.styles import load_all_styles
from utils.visualization import create_bumpy_chart 

from data.api_handlers.football_data_api import load_teams_mapping

from utils.visualization import create_bumpy_chart, create_match_timeline
from data.api_handlers.football_data_api import load_teams_mapping, get_atletico_matches

from data.data_processing.understat_data import get_atletico_data
from utils.visualization import plot_atletico_xg_differential

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
    
    st.write("")
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

# ----------------------------------------------------------------
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
        df_cla = load_liga_positions()
    
        # Inicializar valores por defecto si es la primera vez
        if "highlight_teams" not in st.session_state:
            st.session_state.highlight_teams = ["Club Atlético de Madrid", "Real Madrid CF", "FC Barcelona"]

        # Seleccionar equipos a destacar con estado persistente
        highlight_teams = st.multiselect(
            "Equipos a destacar:",
            df_cla["Equipo"].tolist(),
            default=st.session_state.highlight_teams
        )

        # Guardar la selección actual en session_state
        st.session_state.highlight_teams = highlight_teams
    
        # Crear y mostrar el gráfico
        fig, ax = create_bumpy_chart(df_cla, highlight_teams)
        st.pyplot(fig)
    
    except Exception as e:
        st.error(f"Error al cargar o procesar los datos: {str(e)}")

# ----------------------------------------------------------------
# TAB 2 - Timeline Partidos
with tab2:
    st.subheader("Timeline de Partidos")
    
    @st.cache_data(ttl=3600)
    def load_atletico_matches():    
        # Intentar obtener la API key de Streamlit secrets o variables de entorno
        try:
            # Primero intentar obtener de Streamlit secrets
            api_key = st.secrets["FOOTBALL_DATA_API_KEY"]
        except:
            # Si falla, intentar obtener de variables de entorno
            from dotenv import load_dotenv
            import os
            load_dotenv()
            api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    
        if not api_key:
            st.error("No se encontró la API Key para football-data.org. Verifica tus secrets o .env")
            return None
    
        return get_atletico_matches(api_key)
    
    try:
        matches_df = load_atletico_matches()
        
        if matches_df is not None and not matches_df.empty:
            
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

# ----------------------------------------------------------------
# TAB 3 - Expected Goals
with tab3:
    st.subheader("Análisis xG por Jornada")
    
    # Cargar datos
    try:
        with st.spinner("Cargando datos de xG desde Understat..."):
                        
            df_expcGL, df1 = get_atletico_data()
        
        # Mostrar gráfico
        fig = plot_atletico_xg_differential(df_expcGL, df1)
        st.pyplot(fig)
        
        # Mostrar datos en una tabla expandible
        with st.expander("Ver datos en tabla"):
            st.dataframe(df_expcGL.style.format({
                'xG': '{:.2f}', 
                'xGA': '{:.2f}',
                'xGdif': '{:.2f}',
                'npxG': '{:.2f}',
                'npxGA': '{:.2f}',
                'xpts': '{:.2f}',
                'npxGD': '{:.2f}'
            }))
                
    except Exception as e:
        st.error(f"Error al cargar o procesar los datos de xG: {str(e)}")
        st.error("Asegúrate de tener instalada la librería 'lxml' y 'highlight-text': pip install lxml highlight-text")

current_page = __file__.split('\\')[-1]

# Inicializar y actualizar el historial
if "page_history" not in st.session_state:
    st.session_state.page_history = []

# Actualizar historial solo si es una página nueva
if not st.session_state.page_history or st.session_state.page_history[-1] != current_page:
    st.session_state.page_history.append(current_page)


# ----------------------------------------------------------------
# Crear contenedor para botón de PDF y footer sin línea divisoria

st.markdown("---")
footer_container = st.container()

with footer_container:        
    footer_cols = st.columns([1, 2, 1])
    
    # Columna izquierda - Botón PDF con texto incluido
    with footer_cols[0]:
        if st.button("📑 Exportar Informe PDF", key="generate_pdf"):
            try:
                # Obtener figuras actuales
                figures = {}
    
                # 1. Clasificación (Tab 1) 
                try:
                    if "highlight_teams" in st.session_state and df_cla is not None:
                            
                        # Buscar si hay alguna columna que podría contener nombres de equipos
                        possible_team_columns = [col for col in df_cla.columns if any(word in col.lower() for word in ['equipo', 'team', 'club', 'nombre'])]
                            
                        # Intentar adaptar el DataFrame antes de llamar a create_bumpy_chart
                        df_cla_copy = df_cla.copy()
    
                        # Si no existe 'Equipo' pero hay columnas similares, renombrar la primera
                        if 'Equipo' not in df_cla.columns and possible_team_columns:
                            df_cla_copy.rename(columns={possible_team_columns[0]: 'Equipo'}, inplace=True)
                            st.write(f"Renombrando columna {possible_team_columns[0]} a 'Equipo'")
    
                        # Generar el gráfico con el DataFrame adaptado
                        fig1, _ = create_bumpy_chart(df_cla_copy, st.session_state.highlight_teams)
                        figures["Clasificación LaLiga"] = fig1
                except Exception as e:
                    st.error(f"No se pudo incluir el gráfico de clasificación: {str(e)}")

                # 2. Timeline (Tab 2)
                try:
                    if 'matches_df' in locals() and 'team_mapping' in locals():
                        if matches_df is not None and team_mapping is not None:
                            fig2 = create_match_timeline(matches_df, team_mapping)
                            figures["Timeline Partidos"] = fig2
                except Exception as e:
                    st.warning(f"No se pudo incluir el gráfico de timeline: {str(e)}")
        
                # 3. Análisis xG (Tab 3)
                try:
                    # Obtener datos frescos usando tu función
                
                    df_expcGL_xg, df1_xg = get_atletico_data()
                    fig3 = plot_atletico_xg_differential(df_expcGL, df1_xg)
                    figures["Análisis xG"] = fig3
                except Exception as e:
                    st.warning(f"No se pudo incluir el gráfico xG: {str(e)}")

                # Datos del PDF
                pdf_data = {
                    "Clasificación LaLiga": "Análisis de la evolución de posiciones en la liga",
                    "Timeline Partidos": "Calendario y resultados de partidos disputados",
                    "Análisis xG": "Análisis de Expected Goals acumulado durante la temporada"
                }

                # Generar PDF
                pdf_bytes = export_to_pdf(
                    pdf_data,  
                    figures=figures,  
                    filename=f"Gráficas ATM 24/25 {datetime.now().strftime('%d%m%Y')}.pdf",
                    title="Informe Atlético de Madrid - Visualizaciones 24/25"
                )

                # Guardar PDF en session_state
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.pdf_filename = f"Gráficas ATM 24/25 {datetime.now().strftime('%d%m%Y')}.pdf"
                st.success("PDF generado correctamente")

            except Exception as e:
                st.error(f"Error al generar el PDF: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
            
        # Si hay un PDF generado, mostrar botón de descarga
        if "pdf_bytes" in st.session_state and st.session_state.pdf_bytes:
            download_pdf_button(
                st.session_state.pdf_bytes,
                filename=st.session_state.pdf_filename)
    
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
    # Espacio flexible (empuja los botones hacia abajo)
    st.markdown('<div style="flex: 1;"></div>', unsafe_allow_html=True)
    
    # Corrección de orientación del texto en botones
    st.markdown("""
        <style>
        .stButton button {
            writing-mode: horizontal-tb !important;
            text-align: center !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Botón Back
    if st.button("Back", key="back_button", use_container_width=True):
        if 'page_history' in st.session_state and len(st.session_state.page_history) > 1:
            st.session_state.page_history.pop()
            previous_page = st.session_state.page_history[-1]
            st.switch_page(f"pages/{previous_page}")
    
    # Botón Exit
    if st.button("Exit", key="exit_button", use_container_width=True):
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