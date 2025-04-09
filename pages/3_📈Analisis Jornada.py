import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from datetime import datetime
from pathlib import Path
import traceback
import os
import threading
import time
import LanusStats as ls

from utils.auth import check_auth, logout
from common.pdf_export import export_to_pdf, download_pdf_button

from utils.styles import load_all_styles

from highlight_text import fig_text

from data.jornada_data.url_mapeo import load_partidos_master, load_equipos_master
from data.jornada_data.csv_lectura import load_match_stats, load_partido_stats, process_whoscored_event_data, get_passes_df, get_passes_between_df

from utils.visualization_2 import plot_team_metrics, pass_network_visualization, atleti_color, rival_color  
from utils.visualization_2 import fotmob_match_momentum_plot_atletico
from utils.visualization_2 import plot_xg_timeline, preprocess_xg_data
from utils.visualization_2 import plot_shot_map
from utils.cache import get_fotmob_data, init_cache

# Inicializar caché
init_cache()

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

# Obtener el nombre de la página actual
current_page = __file__.split('\\')[-1]

# Inicializar y actualizar el historial
if "page_history" not in st.session_state:
    st.session_state.page_history = []

# Actualizar historial solo si es una página nueva
if not st.session_state.page_history or st.session_state.page_history[-1] != current_page:
    st.session_state.page_history.append(current_page)

# Inicializar caché en session_state si no existe
if 'momentum_cache' not in st.session_state:
    st.session_state.momentum_cache = {}

def get_momentum_with_cache(fotmob_id, debug=False):
    """Obtiene momentum con caché para mejorar rendimiento"""
    cache_key = f"momentum_{fotmob_id}"
    
    # Si ya está en caché, usarlo
    if cache_key in st.session_state.momentum_cache:
        return st.session_state.momentum_cache[cache_key]
    
    # Si no, obtener nuevos datos
    try:
        fig, ax = fotmob_match_momentum_plot_atletico(fotmob_id, debug=debug)
        
        # Guardar en caché
        st.session_state.momentum_cache[cache_key] = (fig, ax)
        
        return fig, ax
    except Exception as e:
        raise e

# ----------------------------------------------------------------
# CONTENIDO ESPECÍFICO DE LA PÁGINA - ANÁLISIS POR JORNADA
def main():
    # Cargar datos maestros
    try:
        partidos_df = load_partidos_master()
        equipos_df = load_equipos_master()
    
        if partidos_df.empty or equipos_df.empty:
            st.error("No se pudieron cargar los datos maestros")
            return
        
        st.session_state.partidos_df = partidos_df
        st.session_state.equipos_df = equipos_df

        # Selector de jornada con persistencia
        jornadas = partidos_df['formato_jornada'].tolist()
    
        # Inicializar session_state si no existe
        if 'selected_jornada' not in st.session_state:
            st.session_state.selected_jornada = jornadas[0]  # Primera jornada por defecto

        if 'prev_selected_jornada' not in st.session_state:
            st.session_state.prev_selected_jornada = None

        # Encontrar el índice de la jornada guardada en session_state
        try:
            default_index = jornadas.index(st.session_state.selected_jornada)
        except ValueError:
            default_index = 0  
    
        # Mostrar el selectbox con el valor guardado seleccionado
        selected_jornada = st.selectbox(
            "Selecciona una jornada:", 
            jornadas,
            index=default_index,
            key='jornada_selectbox'
        )
    
        # Detectar cambios reales en la selección
        if st.session_state.prev_selected_jornada != selected_jornada:
            st.session_state.prev_selected_jornada = selected_jornada
            st.session_state.selected_jornada = selected_jornada
            
        # Obtener datos del partido
        partido_row = partidos_df[partidos_df['formato_jornada'] == selected_jornada]
        if partido_row.empty:
            st.error(f"No se encontró información para la jornada: {selected_jornada}")
            return
            
        partido_data = partido_row.iloc[0]
        
        # Mostrar información básica del partido
        jornada_num = partido_data['Jornada']
        equipo_local = partido_data['equipo_local']
        equipo_visitante = partido_data['equipo_visitante']
        
        st.write(f"Jornada: {jornada_num}")
        st.write(f"Partido: {equipo_local} vs {equipo_visitante}")
        
        # Buscar información de equipos para los escudos
        local_row = equipos_df[equipos_df['nombre'].str.strip() == equipo_local.strip()]
        visitante_row = equipos_df[equipos_df['nombre'].str.strip() == equipo_visitante.strip()]
        
        local_info = None
        visitante_info = None
        
        if not local_row.empty:
            local_info = local_row.iloc[0].to_dict()

        if not visitante_row.empty:
            visitante_info = visitante_row.iloc[0].to_dict()
                
        # Cargar estadísticas del partido
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

        # ----------------------------------------------------------------
        
        # SECCIÓN DE VISUALIZACIONES - USANDO TABS
        st.header("Visualizaciones avanzadas")
        
        # Crear opciones de visualización como pestañas
        tab1, tab2, tab3, tab4 = st.tabs([
            "Dinámica del partido",
            "Redes de pases",                         
            "Expected Goals (xG)", 
            "Mapas de tiros"
        ])
        
        # Creación de pestañas para seleccionar visualización

        with tab1:
            st.subheader("Match Momentum")

            # Verificar si estamos en una jornada problemática
            is_problematic_jornada = False  # Ya no tenemos jornadas problemáticas

            try:
                # Verificar si tenemos ID de FotMob
                if 'id_fotmob' in partido_data and not pd.isna(partido_data['id_fotmob']):
                    fotmob_id = str(partido_data['id_fotmob'])
            
                    with st.spinner("Cargando datos de momentum..."):
                        fig_mm, ax_mm = fotmob_match_momentum_plot_atletico(fotmob_id, debug=False)
                        st.pyplot(fig_mm)
                else:
                    st.warning(f"No hay ID de FotMob disponible para el partido: {partido_data['equipo_local']} vs {partido_data['equipo_visitante']}")
    
            except Exception as e:
                st.error(f"Error al generar el gráfico de momentum: {str(e)}")
                st.info("Es posible que este partido no tenga datos de momentum disponibles en FotMob.")

        # Mapa de redes de pase 

        with tab2:
            st.subheader("Redes de pases")
            try:
                # Preparar rutas de archivos
                jornada_formato = selected_jornada.replace(' ', '_')
                events_file = f"data/FData/matches/{jornada_formato}_EventData_whoscored.csv"
                players_file = f"data/FData/matches/{jornada_formato}_PlayerData_whoscored.csv"
                teams_file = "data/FData/master/equipos_master.csv"

                # Procesar los datos - usar la función existente
                df_red, dfp_red, team_info = process_whoscored_event_data(events_file, players_file, teams_file)
        
                # Preparar datos para visualización
                passes_df = get_passes_df(df_red)
        
                # Definir colores
                atleti_color = '#172790'  # Azul oscuro para el Atlético de Madrid
                rival_color = '#e60000'   # Rojo para el equipo rival
        
                # Crear figura
                fig, axs = plt.subplots(1, 2, figsize=(20, 12), facecolor="#d4d4d4")
        
                # Procesar y visualizar ambos equipos
                for i, team_name in enumerate([team_info['home_team_name'], team_info['away_team_name']]):
                    # Determinar si este equipo es el Atlético de Madrid
                    is_this_team_atleti = (team_info['is_atleti_home'] and i == 0) or (not team_info['is_atleti_home'] and i == 1)
                    team_color = atleti_color if is_this_team_atleti else rival_color
            
                    # Calcular datos para este equipo usando la función existente
                    passes_between_df, average_locs_df = get_passes_between_df(team_name, passes_df, None, df_red)
            
                    # Dibujar red de pases
                    pass_network_visualization(
                        ax=axs[i],
                        passes_between_df=passes_between_df,
                        average_locs_and_count_df=average_locs_df,
                        teamName=team_name,
                        passes_df=passes_df,
                        home_team=team_info['home_team_name'],
                        away_team=team_info['away_team_name'],
                        team_color=team_color,
                        jornada=selected_jornada  # Añadir el parámetro jornada
                    )
        
                plt.tight_layout()
                st.pyplot(fig)
        
            except Exception as e:
                import traceback
                st.error(f"Error al generar red de pases: {str(e)}")
                st.write(traceback.format_exc())

        # XG visualización

        with tab3:
            st.subheader("Expected Goals (xG)")
    
            with st.spinner("Cargando datos de xG..."):
                try:
                    # Obtener URL del partido desde partido_data
                    url_partido = partido_data.get('url_fbref')
            
                    if url_partido:
                        try:
                            # Cargar datos de fbref
                            df_processed = pd.read_html(url_partido, attrs={'id': 'shots_all'})[0]
                            # Verificar si tennemos datos válidos
                            if df_processed.empty or df_processed.shape[0] < 2:
                                st.warning(f"No hay suficientes datos de tiros para la jornada {selected_jornada}")
                            # Preprocesar datos de xG
                            else:
                                df_xG = preprocess_xg_data(df_processed)

                                if df_xG.empty:
                                    st.warning("No se pudieron procesar los datos xG correctamente")
                                else:
                                    # Crear figura de xG
                                    fig = plot_xg_timeline(df_xG)
                
                                    # Mostrar figura
                                    st.pyplot(fig)

                        except Exception as e:
                            import traceback
                            st.error(f"Error al procesar datos de xG: {str(e)}")
                            st.code(traceback.format_exc())
                            st.warning(f"Estructura de datos no compatible para la jorndad {selected_jornada}")

                    else:
                        st.info("No se encontró URL de partido para cargar datos de xG")
        
                except Exception as e:
                    import traceback 
                    st.error(f"Error al cargar datos de xG: {str(e)}")
                    st.code(traceback.format_exc())
        
        # Representación de tiros de ambos equipos
        
        with tab4:
            st.subheader("Mapas de tiros")
    
            with st.spinner("Cargando datos de tiros..."):
                try:
                    # Verificar si tenemos ID de Understat
                    if 'id_understat' in partido_data and not pd.isna(partido_data['id_understat']):
                        # Convertir a entero y luego a string para eliminar el ".0"
                        understat_id = str(int(float(partido_data['id_understat'])))
                
                        # Función cacheada para obtener datos de tiros
                        @st.cache_data(ttl=3600)
                        def get_cached_shots(id_understat):
                            from data.data_processing.understat_data import get_shot_map
                            return get_shot_map(id_understat)
                
                        # Obtener datos
                        shots_data = get_cached_shots(understat_id)
                
                        if shots_data:
                            col1, col2 = st.columns(2)
                    
                            with col1:
                                local_shots_fig = plot_shot_map(shots_data['local'], partido_data['equipo_local'])
                                st.pyplot(local_shots_fig)
                    
                            with col2:
                                visitante_shots_fig = plot_shot_map(shots_data['visitante'], partido_data['equipo_visitante'])
                                st.pyplot(visitante_shots_fig)                                      
                            
                        else:
                            st.warning(f"No se pudieron obtener datos de tiros para el partido: {partido_data['equipo_local']} vs {partido_data['equipo_visitante']}")
                            st.info("Es posible que este partido no tenga datos disponibles en Understat.")
                    else:
                        st.warning("No hay ID de Understat disponible para este partido")
        
                except Exception as e:
                    import traceback
                    st.error(f"Error al cargar mapas de tiros: {str(e)}")
                    st.code(traceback.format_exc())

    except Exception as e:
        import traceback
        st.error(f"Error general en la aplicación: {str(e)}")
        if 'traceback' in globals():
            st.code(traceback.format_exc())
        else:
            import traceback
            st.code(traceback.format_exc())

# Ejecutar la función principal
main()

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
                # Verificar que tenemos session_state con datos
                if 'partidos_df' not in st.session_state or 'selected_jornada' not in st.session_state:
                    st.warning("No hay datos disponibles. Por favor, cargue la página correctamente.")
                else:
                    # Usar datos de session_state
                    partidos_df = st.session_state.partidos_df
                    selected_jornada = st.session_state.selected_jornada

                # Verificar que tenemos una jornada seleccionada
                if 'selected_jornada' not in st.session_state:
                    st.warning("Primero debe seleccionar una jornada")
                else:
                    # Recopilamos la información del partido actual usando las variables
                    # que ya están disponibles en la función main()
                    figures = {}
                
                    # Preparamos un objeto para guardar las figuras generadas
                    if 'pdf_figures' not in st.session_state:
                        st.session_state.pdf_figures = {}
                
                    # Iniciar la creación del PDF con los datos del partido seleccionado
                    jornada_actual = st.session_state.selected_jornada
                
                    # Recrear información clave del partido (estas variables están en main())
                    selected_jornada = jornada_actual
                    partido_row = partidos_df[partidos_df['formato_jornada'] == selected_jornada]
                
                    if not partido_row.empty:
                        partido_data = partido_row.iloc[0]
                        jornada_num = partido_data['Jornada']
                        equipo_local = partido_data['equipo_local']
                        equipo_visitante = partido_data['equipo_visitante']
                    
                        # 1. Intentar obtener figura de Match Momentum
                        try:
                            if 'id_fotmob' in partido_data and not pd.isna(partido_data['id_fotmob']):
                                fotmob_id = str(partido_data['id_fotmob'])
                                fig_mm, _ = fotmob_match_momentum_plot_atletico(fotmob_id, debug=False)
                                figures["Dinámica del partido"] = fig_mm
                        except Exception as e:
                            st.warning(f"No se pudo incluir la figura de momentum: {str(e)}")
                    
                        # 2. Intentar obtener figura de Red de Pases
                        try:
                            jornada_formato = selected_jornada.replace(' ', '_')
                            events_file = f"data/FData/matches/{jornada_formato}_EventData_whoscored.csv"
                            players_file = f"data/FData/matches/{jornada_formato}_PlayerData_whoscored.csv"
                            teams_file = "data/FData/master/equipos_master.csv"
                        
                            df_red, dfp_red, team_info = process_whoscored_event_data(events_file, players_file, teams_file)
                            passes_df = get_passes_df(df_red)
                        
                            # Colores para los equipos
                            atleti_color = '#172790'
                            rival_color = '#e60000'
                        
                            # Crear figura para PDF
                            passes_fig, axs = plt.subplots(1, 2, figsize=(20, 12), facecolor="#d4d4d4")
                        
                            for i, team_name in enumerate([team_info['home_team_name'], team_info['away_team_name']]):
                                is_this_team_atleti = (team_info['is_atleti_home'] and i == 0) or (not team_info['is_atleti_home'] and i == 1)
                                team_color = atleti_color if is_this_team_atleti else rival_color
                            
                                passes_between_df, average_locs_df = get_passes_between_df(team_name, passes_df, None, df_red)
                            
                                pass_network_visualization(
                                    ax=axs[i],
                                    passes_between_df=passes_between_df,
                                    average_locs_and_count_df=average_locs_df,
                                    teamName=team_name,
                                    passes_df=passes_df,
                                    home_team=team_info['home_team_name'],
                                    away_team=team_info['away_team_name'],
                                    team_color=team_color,
                                    jornada=selected_jornada
                                )
                        
                            plt.tight_layout()
                            figures["Redes de pases"] = passes_fig
                        except Exception as e:
                            st.warning(f"No se pudo incluir la figura de red de pases: {str(e)}")
                    
                        # 3. Intentar obtener figura de xG
                        try:
                            url_partido = partido_data.get('url_fbref')
                        
                            if url_partido:
                                df_processed = pd.read_html(url_partido, attrs={'id': 'shots_all'})[0]
                            
                                if not df_processed.empty and df_processed.shape[0] >= 2:
                                    df_xG = preprocess_xg_data(df_processed)
                                
                                    if not df_xG.empty:
                                        xg_fig = plot_xg_timeline(df_xG)
                                        figures["Expected Goals (xG)"] = xg_fig
                        except Exception as e:
                            st.warning(f"No se pudo incluir la figura de xG: {str(e)}")
                    
                        # 4. Intentar obtener mapa de tiros
                        try:
                            if 'id_understat' in partido_data and not pd.isna(partido_data['id_understat']):
                                understat_id = str(int(float(partido_data['id_understat'])))
                            
                                # Importar la función directamente
                                from data.data_processing.understat_data import get_shot_map
                                shots_data = get_shot_map(understat_id)
                            
                                if shots_data:
                                    local_fig = plot_shot_map(shots_data['local'], partido_data['equipo_local'])
                                    visitante_fig = plot_shot_map(shots_data['visitante'], partido_data['equipo_visitante'])
                                
                                    figures["Mapa de tiros Local"] = local_fig
                                    figures["Mapa de tiros Visitante"] = visitante_fig
                        except Exception as e:
                            st.warning(f"No se pudo incluir los mapas de tiros: {str(e)}")
                    
                        # 5. Datos para el PDF
                        # Obtener estadísticas del partido
                        partido_str = f"{equipo_local}-{equipo_visitante}"
                        match_stats_pdf = load_match_stats(jornada=jornada_num, partido=partido_str)
                    
                        # Crear diccionario con datos para PDF
                        pdf_data = {
                            "Información del Partido": f"{equipo_local} vs {equipo_visitante} - Jornada {jornada_num}"
                        }
                    
                        # Añadir estadísticas si existen
                        if match_stats_pdf is not None and not match_stats_pdf.empty:
                            pdf_data["Estadísticas"] = "Métricas clave del encuentro"
                            pdf_data["Tabla de Estadísticas"] = match_stats_pdf
                    
                        # Añadir descripciones para las figuras
                        if "Dinámica del partido" in figures:
                            pdf_data["Dinámica del partido"] = "Análisis del momentum del partido mostrando los momentos clave"
                    
                        if "Redes de pases" in figures:
                            pdf_data["Redes de pases"] = "Visualización de las conexiones entre jugadores durante el partido"
                    
                        if "Expected Goals (xG)" in figures:
                            pdf_data["Expected Goals (xG)"] = "Análisis de las oportunidades de gol generadas por cada equipo"
                    
                        if "Mapa de tiros Local" in figures:
                            pdf_data["Mapa de tiros Local"] = f"Distribución y calidad de los tiros de {equipo_local}"
                    
                        if "Mapa de tiros Visitante" in figures:
                            pdf_data["Mapa de tiros Visitante"] = f"Distribución y calidad de los tiros de {equipo_visitante}"
                    
                        # 6. Generar PDF
                        filename = f"Analisis_{equipo_local}_vs_{equipo_visitante}_J{jornada_num}_{datetime.now().strftime('%d%m%Y')}.pdf"
                        pdf_bytes = export_to_pdf(
                            pdf_data,
                            figures=figures,
                            filename=filename,
                            title=f"Análisis Atlético de Madrid - Jornada {jornada_num}"
                        )
                    
                        # Guardar en session_state para el botón de descarga
                        st.session_state.pdf_bytes = pdf_bytes
                        st.session_state.pdf_filename = filename
                        st.success("PDF generado correctamente")
                    else:
                        st.error(f"No se encontró información para la jornada: {jornada_actual}")
            
            except Exception as e:
                st.error(f"Error al generar el PDF: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
    
        # Si hay un PDF generado, mostrar el botón de descarga
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
    