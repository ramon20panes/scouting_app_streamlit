import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from datetime import datetime
from pathlib import Path
import traceback
import os

from utils.auth import check_auth, logout
from common.pdf_export import export_to_pdf, download_pdf_button

from utils.styles import load_all_styles

from data.jornada_data.url_mapeo import load_partidos_master, load_equipos_master
from data.jornada_data.csv_lectura import load_match_stats, load_partido_stats, process_whoscored_event_data, get_passes_df, get_passes_between_df
from data.jornada_data.func_escraper import get_passing_network, get_xg_data, get_match_momentum, get_shot_map
from utils.visualization_2 import plot_team_metrics, pass_network_visualization, atleti_color, rival_color # plot_xg_comparison, plot_match_momentum, plot_shot_map
 
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
    # 1. Cargar datos maestros
    try:
        partidos_df = load_partidos_master()
        equipos_df = load_equipos_master()
        
        if partidos_df.empty or equipos_df.empty:
            st.error("No se pudieron cargar los datos maestros")
            return
            
        # 2. Selector de jornada simplificado
        jornadas = partidos_df['formato_jornada'].tolist()
        selected_jornada = st.selectbox("Selecciona una jornada:", jornadas)
        
        # 3. Obtener datos del partido
        partido_row = partidos_df[partidos_df['formato_jornada'] == selected_jornada]
        if partido_row.empty:
            st.error(f"No se encontró información para la jornada: {selected_jornada}")
            return
            
        partido_data = partido_row.iloc[0]
        
        # 4. Mostrar información básica del partido
        jornada_num = partido_data['Jornada']
        equipo_local = partido_data['equipo_local']
        equipo_visitante = partido_data['equipo_visitante']
        
        st.write(f"Jornada: {jornada_num}")
        st.write(f"Partido: {equipo_local} vs {equipo_visitante}")
        
        # 5. Buscar información de equipos para los escudos
        local_row = equipos_df[equipos_df['nombre'].str.strip() == equipo_local.strip()]
        visitante_row = equipos_df[equipos_df['nombre'].str.strip() == equipo_visitante.strip()]
        
        local_info = None
        visitante_info = None
        
        if not local_row.empty:
            local_info = local_row.iloc[0].to_dict()
            # Corregir la clave para ruta_escudo si tiene espacios extra
            if ' ruta_escudo' in local_info:
                local_info['ruta_escudo'] = local_info[' ruta_escudo'].strip("'")
            
        if not visitante_row.empty:
            visitante_info = visitante_row.iloc[0].to_dict()
            # Corregir la clave para ruta_escudo si tiene espacios extra
            if ' ruta_escudo' in visitante_info:
                visitante_info['ruta_escudo'] = visitante_info[' ruta_escudo'].strip("'")
                
        # 7. Cargar estadísticas del partido
        partido_str = f"{equipo_local}-{equipo_visitante}"
        
        # Cargar estadísticas usando nuestra función mejorada
        match_stats = load_match_stats(jornada=jornada_num, partido=partido_str)
        
        if match_stats is not None and not match_stats.empty:
            # Mostrar tabla de estadísticas si tenemos datos válidos
            if local_info and visitante_info:
                # Usar tu función plot_team_metrics para mostrar la tabla
                plot_team_metrics(match_stats, local_info, visitante_info)
            else:
                st.warning("No se pudo mostrar la tabla de estadísticas porque falta información de los equipos")
        else:
            st.warning(f"No se encontraron estadísticas para el partido: {partido_str}")
        
        # 8. SECCIÓN DE VISUALIZACIONES - USANDO TABS
        st.header("Visualizaciones avanzadas")
        
        # Crear opciones de visualización como pestañas
        tab1, tab2, tab3, tab4 = st.tabs([
            "Redes de pases", 
            "Expected Goals (xG)", 
            "Dinámica del partido", 
            "Mapas de tiros"
        ])
        
        # En cada pestaña, colocamos la visualización correspondiente
        with tab1:
            st.subheader("Redes de pases")
    
            try:
                                # Reemplazar el espacio con un guion bajo
                jornada_formato = selected_jornada.replace(' ', '_')
        
                # Imprimir rutas de archivos
                events_file = f"data/FData/matches/{jornada_formato}_EventData_whoscored.csv"
                players_file = f"data/FData/matches/{jornada_formato}_PlayerData_whoscored.csv"

                # Procesar los datos de eventos y jugadores
                df, dfp, teams_dict = process_whoscored_event_data(events_file, players_file)
        
                # Procesar los datos de eventos y jugadores
                df, dfp, teams_dict = process_whoscored_event_data(
                    f"data/FData/matches/{jornada_formato}_EventData_whoscored.csv", 
                    f"data/FData/matches/{jornada_formato}_PlayerData_whoscored.csv"
                )
        
                # Preparar datos para visualización de redes de pases
                passes_df = get_passes_df(df)
        
                # Nombres de equipos
                team_names = list(teams_dict.values())
        
                # Asignar colores basados en si el equipo es el Atleti
                if 'Atletico' in team_names[0]:  # Si el Atleti es local
                    hcol = atleti_color
                    acol = rival_color
                    hteamName = team_names[0]
                    ateamName = team_names[1]
                else:  # Si el Atleti es visitante
                    hcol = rival_color
                    acol = atleti_color
                    hteamName = team_names[1]
                    ateamName = team_names[0]
        
                # Generar visualizaciones
                fig, axs = plt.subplots(1, 2, figsize=(20, 10), facecolor="#d4d4d4")
        
                home_passes_between_df, home_average_locs_and_count_df = get_passes_between_df(
                    team_names[0], passes_df, dfp, df
                )
                away_passes_between_df, away_average_locs_and_count_df = get_passes_between_df(
                    team_names[1], passes_df, dfp, df
                )
        
                # Visualización
                pass_network_stats_home = pass_network_visualization(
                    axs[0], home_passes_between_df, home_average_locs_and_count_df, 
                    hcol, team_names[0], passes_df=passes_df, 
                    hteamName=hteamName, ateamName=ateamName
                )
                pass_network_stats_away = pass_network_visualization(
                    axs[1], away_passes_between_df, away_average_locs_and_count_df, 
                    acol, team_names[1], passes_df=passes_df, 
                    hteamName=hteamName, ateamName=ateamName
                )
        
                plt.tight_layout()
                st.pyplot(fig)
    
            except Exception as e:
                st.error(f"Error al generar red de pases: {str(e)}")
                st.write(traceback.format_exc())
        
        with tab2:
            st.subheader("Expected Goals (xG)")
            st.info("Visualización Xg próximamente")
            """
            with st.spinner("Cargando datos de xG..."):
                try:
                    # Función de caché para xG
                    @st.cache_data(ttl=3600)
                    def get_cached_xg_data(id_understat):
                        return get_xg_data(id_understat)
                    
                    id_understat = partido_data.get('id_understat')
                    if id_understat:
                        xg_data = get_cached_xg_data(id_understat)
                        
                        if xg_data and local_info and visitante_info:
                            fig = plot_xg_comparison(xg_data, local_info, visitante_info)
                            st.pyplot(fig)
                        else:
                            st.info("Datos de xG no disponibles para este partido")
                    else:
                        st.info("No se encontró ID de Understat para este partido")
                except Exception as e:
                    st.error(f"Error al cargar datos de xG: {str(e)}")
        """
        
        with tab3:
            st.subheader("Dinámica del partido")
            st.info("Visualización Match Momentum próximamente")
            """""
            with st.spinner("Cargando datos de momentum..."):
                try:
                    # Función de caché para momentum
                    @st.cache_data(ttl=3600)
                    def get_cached_momentum(id_fotmob):
                        return get_match_momentum(id_fotmob)
                    
                    id_fotmob = partido_data.get('id_fotmob')
                    if id_fotmob:
                        momentum_data = get_cached_momentum(id_fotmob)
                        
                        if momentum_data:
                            fig = plot_match_momentum(momentum_data, equipo_local, equipo_visitante)
                            st.pyplot(fig)
                        else:
                            st.info("Datos de dinámica no disponibles para este partido")
                    else:
                        st.info("No se encontró ID de Fotmob para este partido")
                except Exception as e:
                    st.error(f"Error al cargar datos de dinámica: {str(e)}")
        """
        
        with tab4:
            st.subheader("Mapas de tiros")
            st.info("Visualización Mapas de Tiros próximamente")
            """
            with st.spinner("Cargando datos de tiros..."):
                try:
                    # Función de caché para mapas de tiros
                    @st.cache_data(ttl=3600)
                    def get_cached_shots(id_understat):
                        return get_shot_map(id_understat)
                    
                    id_understat = partido_data.get('id_understat')
                    if id_understat:
                        shots_data = get_cached_shots(id_understat)
                        
                        if shots_data and local_info and visitante_info:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"{equipo_local} - Mapa de tiros")
                                local_shots_fig = plot_shot_map(shots_data['local'], equipo_local)
                                st.pyplot(local_shots_fig)
                            
                            with col2:
                                st.write(f"{equipo_visitante} - Mapa de tiros")
                                visitante_shots_fig = plot_shot_map(shots_data['visitante'], equipo_visitante)
                                st.pyplot(visitante_shots_fig)
                        else:
                            st.info("Datos de tiros no disponibles para este partido")
                    else:
                        st.info("No se encontró ID de Understat para este partido")
                except Exception as e:
                    st.error(f"Error al cargar mapas de tiros: {str(e)}")
        """
    
    except Exception as e:
        st.error(f"Error general: {str(e)}")
        import traceback
        st.write(traceback.format_exc())

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
    