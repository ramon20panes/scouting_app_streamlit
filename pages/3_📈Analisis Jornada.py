import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from datetime import datetime
from pathlib import Path

from utils.auth import check_auth, logout
from common.pdf_export import export_to_pdf, download_pdf_button

from utils.styles import load_all_styles

from data.jornada_data.url_mapeo import load_partidos_master, load_equipos_master
from data.jornada_data.csv_lectura import load_match_stats
from data.jornada_data.func_escraper import get_passing_network, get_xg_data, get_match_momentum, get_shot_map
from utils.visualization_2 import plot_team_metrics, plot_passing_network, plot_xg_comparison, plot_match_momentum, plot_shot_map

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

# Título con escudo (modificado para ser más compacto)
col_title, col_logo = st.columns([5, 1])

with col_title:
    st.write("")
    st.markdown("""
        <h2 style='text-align: left; margin-top: -15px; margin-bottom: -10px;'>
            Análisis Post_Partido
        </h2>
    """, unsafe_allow_html=True)

with col_logo:
    st.write("")  # Esto añade un pequeño espacio vertical
    st.image(ESCUDO_PATH, width=70)  # Reducir el tamaño del escudo

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

# Obtener el nombre de la página actual
current_page = __file__.split('\\')[-1]

# Inicializar y actualizar el historial
if "page_history" not in st.session_state:
    st.session_state.page_history = []

# Actualizar historial solo si es una página nueva
if not st.session_state.page_history or st.session_state.page_history[-1] != current_page:
    st.session_state.page_history.append(current_page)

# CONTENIDO ESPECÍFICO DE LA PÁGINA - ANÁLISIS POR JORNADA
def main():
    # Cargar datos maestros
    try:
        partidos_df = load_partidos_master()
        equipos_df = load_equipos_master()

        if partidos_df.empty:
            st.error("No se pudieron cargar los datos de partidos")
        else:
            # Mostrar las columnas disponibles para diagnóstico
            st.write("Columnas disponibles:", partidos_df.columns.tolist())
    
            # Usar el nombre de columna correcto para el selector de jornada
            column_to_use = None
            for possible_column in ['formato_jornada', 'Formato_jornada', 'formato jornada', 'Jornada']:
                if possible_column in partidos_df.columns:
                    column_to_use = possible_column
                    break
    
            if column_to_use:
                jornadas = partidos_df[column_to_use].tolist()
                selected_jornada = st.selectbox(
                    "Selecciona una jornada:", 
                    jornadas,
                    format_func=lambda x: x
                )
                
                # 2. Obtener datos del partido seleccionado
                partido_data = partidos_df[partidos_df[column_to_use] == selected_jornada].iloc[0]
    
                # Este es el código de diagnóstico que debes insertar:
                equipo_local = partido_data['equipo_local']
                equipo_visitante = partido_data['equipo_visitante']

                st.write(f"Buscando equipos: '{equipo_local}' y '{equipo_visitante}'")

                # Veamos si los nombres de equipo coinciden exactamente
                if 'nombre' in equipos_df.columns:
                    equipos_nombres = equipos_df['nombre'].tolist()
                    st.write(f"Valores en columna 'nombre': {equipos_nombres}")
    
                    # Verificar si los equipos existen exactamente
                    if equipo_local in equipos_nombres:
                        local_info = equipos_df[equipos_df['nombre'] == equipo_local].iloc[0].to_dict()
                    else:
                        st.error(f"No se encontró el equipo local '{equipo_local}' exactamente en la lista de nombres")
                        # Buscar coincidencias parciales
                        matches = [e for e in equipos_nombres if equipo_local in e or e in equipo_local]
                        if matches:
                            st.write(f"Posibles coincidencias: {matches}")
                            local_info = equipos_df[equipos_df['nombre'] == matches[0]].iloc[0].to_dict()
                        else:
                            local_info = None
    
                    if equipo_visitante in equipos_nombres:
                        visitante_info = equipos_df[equipos_df['nombre'] == equipo_visitante].iloc[0].to_dict()
                    else:
                        st.error(f"No se encontró el equipo visitante '{equipo_visitante}' exactamente en la lista de nombres")
                        # Buscar coincidencias parciales
                        matches = [e for e in equipos_nombres if equipo_visitante in e or e in equipo_visitante]
                        if matches:
                            st.write(f"Posibles coincidencias: {matches}")
                            visitante_info = equipos_df[equipos_df['nombre'] == matches[0]].iloc[0].to_dict()
                        else:
                            visitante_info = None
            else:
                st.error("No se encontró la columna 'nombre' en el DataFrame de equipos")
                st.write("Columnas disponibles:", equipos_df.columns.tolist())
                local_info = None
                visitante_info = None
                
                # 4. Sección de visualizaciones adicionales
                st.header("Visualizaciones avanzadas")
                
                    # Crear opciones de visualización como botones o selectbox
                visualization_options = [
                    "Redes de pases", 
                    "Expected Goals (xG)", 
                    "Dinámica del partido", 
                    "Mapas de tiros"
                ]
                
                selected_viz = st.radio(
                    "Selecciona una visualización:",
                    visualization_options,
                    horizontal=True
                )
                
                # Contenedor para la visualización seleccionada
                viz_container = st.container()
                
                with viz_container:
                    if selected_viz == "Redes de pases":
                        # El resto del código para visualizaciones...
                        with st.spinner("Cargando datos de pases..."):
                            try:
                                # Función de caché para redes de pases
                                @st.cache_data(ttl=3600)
                                def get_cached_passing_network(partido_data):
                                    match_id = partido_data.get('id_whoscored')  # O el ID que uses para esta visualización
                                    return get_passing_network(match_id)
                                
                                passing_data = get_cached_passing_network(partido_data)
                                
                                if passing_data:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.subheader(f"{local_info['nombre']} - Red de pases")
                                        local_network_fig = plot_passing_network(
                                            passing_data['local'], 
                                            local_info['nombre']
                                        )
                                        st.pyplot(local_network_fig)
                                    
                                    with col2:
                                        st.subheader(f"{visitante_info['nombre']} - Red de pases")
                                        visitante_network_fig = plot_passing_network(
                                            passing_data['visitante'], 
                                            visitante_info['nombre']
                                        )
                                        st.pyplot(visitante_network_fig)
                                else:
                                    st.warning("No se pudieron obtener datos de pases para este partido.")
                            except Exception as e:
                                st.error(f"Error al cargar redes de pases: {str(e)}")
                    
                    elif selected_viz == "Expected Goals (xG)":
                        with st.spinner("Cargando datos de xG..."):
                            try:
                                # Similar al código anterior para xG
                                # ...
                                st.info("Visualización de Expected Goals en desarrollo")
                            except Exception as e:
                                st.error(f"Error al cargar datos de xG: {str(e)}")
                    
                    elif selected_viz == "Dinámica del partido":
                        with st.spinner("Cargando datos de momentum..."):
                            try:
                                # Similar al código anterior para momentum
                                # ...
                                st.info("Visualización de dinámica de partido en desarrollo")
                            except Exception as e:
                                st.error(f"Error al cargar datos de dinámica: {str(e)}")
                    
                    elif selected_viz == "Mapas de tiros":
                        with st.spinner("Cargando mapas de tiros..."):
                            try:
                                # Similar al código anterior para mapas de tiros
                                # ...
                                st.info("Visualización de mapas de tiros en desarrollo")
                            except Exception as e:
                                st.error(f"Error al cargar mapas de tiros: {str(e)}")
                    else:
                        st.error("No se encontró una columna adecuada para las jornadas")
    except Exception as e:
        st.error(f"Error general: {str(e)}")

# Ejecutar la función principal
main()

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
                "Gráficos": "Resumen de visualizaciones generadas",
                # Añade los datos específicos de esta página
            }

            # Generar PDF
            pdf_bytes = export_to_pdf(
                pdf_data, 
                filename=f"informe_atm_{datetime.now().strftime('%d%m%Y')}.pdf",
                title="Informe Atlético de Madrid - Métricas 24/25"
            )
            
            # Mostrar botón de descarga - MOVIDO DENTRO DEL BLOQUE IF
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
    