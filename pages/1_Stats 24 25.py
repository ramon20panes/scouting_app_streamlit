import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import sys
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from utils.auth import check_auth, logout
from common.database import get_players_atleti, categorize_metrics
from common.pdf_export import export_to_pdf
from common.pdf_export import download_pdf_button

# Configuración de la página
st.set_page_config(
    page_title="Atlético de Madrid 24/25",
    page_icon="⚽",
    layout="wide"
)

# Verificar autenticación
if not check_auth():
    st.switch_page("Aplic_Direcc_Deport.py")

ESCUDO_PATH = Path("assets/escudos/atm.png")

# Título con escudo
col_title, col_logo = st.columns([1, 1])

with col_title:
    st.markdown("""
        <h2 style='text-align: right; margin-top: -10px;'>
            Métricas 24/25
        </h2>
    """, unsafe_allow_html=True)

with col_logo:
    st.image(ESCUDO_PATH, width=50)

# Cargar datos de jugadores del Atlético
@st.cache_data(ttl=3600)
def load_data():
    return get_players_atleti()

player_data = load_data()

if player_data.empty:
    st.error("No se pudieron cargar los datos de los jugadores. Verifique la conexión a la base de datos.")
else:
    # Categorizar métricas
    categorized_metrics = categorize_metrics(player_data.columns)
    
    filter_col1, filter_col2 = st.columns([3, 1])
    
    with filter_col1:
        # Selector de categorías para la tabla
        metric_categories = st.multiselect(
            "Grupo métricas:",
            ["Ataque", "Pases", "Posesión", "Defensa", "Disciplina"],
            default=["Ataque"]
        )
        
        # Recopilar métricas de las categorías seleccionadas
        selected_table_metrics = []
        for category in metric_categories:
            selected_table_metrics.extend(categorized_metrics.get(category, []))
    
    with filter_col2:
        # Slider de minutos para la tabla
        max_minutes = int(player_data['Minutos'].max()) if not player_data.empty else 3000
        min_minutes, max_minutes_selected = st.slider(
            "Minuto de juego",
            min_value=0,
            max_value=max_minutes,
            value=(0, max_minutes)
        )
    
    # Filtrar jugadores por minutos
    filtered_players = player_data[(player_data['Minutos'] >= min_minutes) & 
                                   (player_data['Minutos'] <= max_minutes_selected)]
    
    # Definir métricas básicas (corrigiendo los nombres para que coincidan con los de la base de datos)
    basic_metrics = ["Jugador", "Posición", "Partidos", "Titularidades", "Minutos"]

    # Mantener las métricas básicas sí o sí y agregar solo las seleccionadas que existan en los datos
    display_columns = basic_metrics + [col for col in selected_table_metrics if col in filtered_players.columns]

    # Mostrar tabla solo con las columnas seleccionadas y existentes
    st.dataframe(
        filtered_players[display_columns].style.background_gradient(
            cmap='RdYlGn',
            subset=[m for m in selected_table_metrics if m in filtered_players.columns]
        ),
        use_container_width=True,
        height=300
    )
    
    # SECCIÓN 2: Rankings con slider de minutos
    col_title2, col_logo2 = st.columns([1, 1])
    with col_title2:
        st.markdown("""
            <h2 style='text-align: right; margin-top: -10px;'>
                Ránkings
            </h2>
        """, unsafe_allow_html=True)

    with col_logo2:
        st.image(ESCUDO_PATH, width=50)
    
    # Fila para controles de ranking
    rank_control_cols = st.columns([3, 1])
    
    with rank_control_cols[0]:
        # Todas las métricas para rankings (excluyendo las básicas)
        all_metrics = []
        for category, metrics in categorized_metrics.items():
            if category != "Básicas":
                all_metrics.extend(metrics)
        
        # Tres selectores para métricas de ranking
        rank_metric_cols = st.columns(3)
        with rank_metric_cols[0]:
            ranking_metric1 = st.selectbox(" ",all_metrics, 
                                          index=all_metrics.index("Goles") if "Goles" in all_metrics else 0)
        with rank_metric_cols[1]:
            ranking_metric2 = st.selectbox("Selecciona variables:", all_metrics, 
                                          index=all_metrics.index("Asistencias") if "Asistencias" in all_metrics else 0)
        with rank_metric_cols[2]:
            ranking_metric3 = st.selectbox(" ",all_metrics, 
                                          index=all_metrics.index("Pases clave") if "Pases clave" in all_metrics else 0)
    
    with rank_control_cols[1]:
        # Slider de minutos para rankings
        rank_min, rank_max = st.slider(
            "Mín Minutos",
            min_value=0,
            max_value=max_minutes,
            value=(100, max_minutes)  # Por defecto filtramos jugadores con menos de 100 minutos
        )
    
    # Filtrar jugadores para rankings por minutos
    rank_players = player_data[(player_data['Minutos'] >= rank_min) & 
                               (player_data['Minutos'] <= rank_max)]
    
    # Mostrar rankings en tres columnas
    ranking_cols = st.columns(3)
    
    with ranking_cols[0]:
        # Top jugadores para métrica 1
        top_players1 = rank_players.sort_values(by=ranking_metric1, ascending=False).head(3)
        st.markdown(f"<h5 style='text-align: center;'>Top {ranking_metric1}</h5>", unsafe_allow_html=True)
        for i, (_, player) in enumerate(top_players1.iterrows(), 1):
            st.markdown(f"{i}. {player['Jugador']} - {player[ranking_metric1]}")
    
    with ranking_cols[1]:
        # Top jugadores para métrica 2
        top_players2 = rank_players.sort_values(by=ranking_metric2, ascending=False).head(3)
        st.markdown(f"<h5 style='text-align: center;'>Top {ranking_metric2}</h5>", unsafe_allow_html=True)
        for i, (_, player) in enumerate(top_players2.iterrows(), 1):
            st.markdown(f"{i}. {player['Jugador']} - {player[ranking_metric2]}")
    
    with ranking_cols[2]:
        # Top jugadores para métrica 3
        top_players3 = rank_players.sort_values(by=ranking_metric3, ascending=False).head(3)
        st.markdown(f"<h5 style='text-align: center;'>Top {ranking_metric3}</h5>", unsafe_allow_html=True)
        for i, (_, player) in enumerate(top_players3.iterrows(), 1):
            st.markdown(f"{i}. {player['Jugador']} - {player[ranking_metric3]}")
    
    # SECCIÓN 3: Área de visualizaciones
    col_title2, col_logo2 = st.columns([1, 1])
    with col_title2:
        st.markdown("""
            <h2 style='text-align: right; margin-top: -10px;'>
                Visualizaciones
            </h2>
        """, unsafe_allow_html=True)

    with col_logo2:
        st.image(ESCUDO_PATH, width=50)
    
    # Tres columnas para las visualizaciones
    viz_col1, viz_col2, viz_col3 = st.columns(3)
    
    with viz_col1:
        st.markdown("<h4 style='text-align: center;'>Clasificación LaLiga</h4>", unsafe_allow_html=True)
        st.info("Gráfico de clasificación con liga_positions_24_25.csv")
    
    with viz_col2:
        st.markdown("<h4 style='text-align: center;'>Timeline LaLiga 24/25</h4>", unsafe_allow_html=True)
        st.info("Timeline con datos de la API")
    
    with viz_col3:
        st.markdown("<h4 style='text-align: center;'>Expected Goals (xG)</h4>", unsafe_allow_html=True)
        st.info("xG con datos de Understat")

# Obtener el nombre de la página actual
current_page = __file__.split('\\')[-1]

# Inicializar y actualizar el historial
if "page_history" not in st.session_state:
    st.session_state.page_history = []

# Actualizar historial solo si es una página nueva
if not st.session_state.page_history or st.session_state.page_history[-1] != current_page:
    st.session_state.page_history.append(current_page)

# Sidebar con navegación al final
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