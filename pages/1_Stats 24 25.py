import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import sys
from pathlib import Path
from utils.auth import check_auth, logout
from common.database import get_players_atleti, categorize_metrics
from common.pdf_export import export_to_pdf, download_pdf_button
import base64
from datetime import datetime
from utils.styles import load_all_styles

# Configuración de la página
st.set_page_config(
    page_title="Atlético de Madrid 24/25",
    page_icon="⚽",
    layout="wide"
)

# Cargar estilos al principio del archivo
load_all_styles()

# Mostrar sidebar explícitamente - COLOCADO DESPUÉS DE LOAD_ALL_STYLES
st.markdown("""
<style>
[data-testid="stSidebar"][aria-expanded="false"],
[data-testid="stSidebar"][aria-expanded="true"],
div[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative !important;
    z-index: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if not check_auth():
    st.switch_page("Aplic_Direcc_Deport.py")

# Cargar estilos al principio del archivo
load_all_styles()

ESCUDO_PATH = Path("assets/escudos/atm.png")
    
# Título con escudo
col_title, col_logo = st.columns([4, 1])

with col_title:
    st.markdown("""
        <h2 style='text-align: left; margin-top: -10px;'>
            Métricas 24/25
        </h2>
    """, unsafe_allow_html=True)

with col_logo:
    st.image(ESCUDO_PATH, width=100)

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
    
    filter_col1, filter_col2 = st.columns([4, 1])
    
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
        height=400
    )
    
    # SECCIÓN 2: Rankings con slider de minutos
    st.markdown("""
        <h2 style='text-align: left; margin-top: -10px;'>
            Ránkings
        </h2>
    """, unsafe_allow_html=True)

    
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
        top_players1 = rank_players.sort_values(by=ranking_metric1, ascending=False).head(5)
        st.markdown(f"<h5 style='text-align: center;'>Top {ranking_metric1}</h5>", unsafe_allow_html=True)
        for i, (_, player) in enumerate(top_players1.iterrows(), 1):
            st.markdown(f"{i}. {player['Jugador']} - {player[ranking_metric1]}")
    
    with ranking_cols[1]:
        # Top jugadores para métrica 2
        top_players2 = rank_players.sort_values(by=ranking_metric2, ascending=False).head(5)
        st.markdown(f"<h5 style='text-align: center;'>Top {ranking_metric2}</h5>", unsafe_allow_html=True)
        for i, (_, player) in enumerate(top_players2.iterrows(), 1):
            st.markdown(f"{i}. {player['Jugador']} - {player[ranking_metric2]}")
    
    with ranking_cols[2]:
        # Top jugadores para métrica 3
        top_players3 = rank_players.sort_values(by=ranking_metric3, ascending=False).head(5)
        st.markdown(f"<h5 style='text-align: center;'>Top {ranking_metric3}</h5>", unsafe_allow_html=True)
        for i, (_, player) in enumerate(top_players3.iterrows(), 1):
            st.markdown(f"{i}. {player['Jugador']} - {player[ranking_metric3]}")        
    
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
    # Usa un espacio para crear más separación con el contenido anterior
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    
    footer_cols = st.columns([1, 2, 1])
    
    # Columna izquierda - Botón PDF con texto incluido
    with footer_cols[0]:
        if st.button("📑 Exportar Informe PDF", key="generate_pdf"):
            # Crear diccionario con datos para el PDF
            pdf_data = {
                "Información General": "Informe de métricas del Atlético de Madrid temporada 24/25",
                f"Tabla de Jugadores ({', '.join(metric_categories)})": filtered_players[display_columns],
                f"Ranking de {ranking_metric1}": top_players1[['Jugador', ranking_metric1]],
                f"Ranking de {ranking_metric2}": top_players2[['Jugador', ranking_metric2]],
                f"Ranking de {ranking_metric3}": top_players3[['Jugador', ranking_metric3]]
            }
            
            # Generar PDF
            pdf_bytes = export_to_pdf(
                pdf_data, 
                filename=f"informe_atm_{datetime.now().strftime('%d%m%Y')}.pdf",
                title="Informe Atlético de Madrid - Métricas 24/25"
            )
            
            # Mostrar botón de descarga
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.pdf_filename = f"informe_atm_{datetime.now().strftime('%d%m%Y')}.pdf"
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

    # CSS adicional para que el footer se vea correctamente con el botón PDF
st.markdown("""
    <style>
    /* Ajustes para la sección del footer */
    .author-container {
        position: relative !important;
        text-align: right;
        margin-top: 20px;
    }
    .footer-container {
        position: relative !important;
        text-align: right;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

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