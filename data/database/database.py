import streamlit as st
import sqlite3
import pandas as pd
import os
from pathlib import Path

# Obtener la ruta absoluta a la base de datos
DB_PATH = Path(__file__).parent.parent / "FData/stats/stats_big5_24_25.db"

def get_db_path():
    """
    Obtiene la ruta de la base de datos de manera más flexible
    """
    # Lista de posibles rutas
    possible_paths = [
        Path(__file__).parent.parent / "FData/stats/stats_big5_24_25.db",
        Path("data/FData/stats/stats_big5_24_25.db"),
        Path("./data/FData/stats/stats_big5_24_25.db"),
        Path("/mount/src/scouting_app_streamlit/data/FData/stats/stats_big5_24_25.db"),
        Path(os.getcwd()) / "data/FData/stats/stats_big5_24_25.db",
        Path(os.path.dirname(os.path.dirname(__file__))) / "FData/stats/stats_big5_24_25.db"
    ]
    
    # Buscar la base de datos en las rutas posibles
    for path in possible_paths:
        if path.exists():
            return path
    
    # Si llegamos aquí, la base de datos no se encontró
    st.error("No se encontró la base de datos en ninguna de las rutas posibles.")
    return None

def get_connection():
    """Establece conexión con la base de datos SQLite."""
    DB_PATH = get_db_path()
    
    if DB_PATH is None:
        st.error("No se puede establecer conexión con la base de datos")
        return None
    
    try:        
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

def get_players_atleti():
    """
    Obtiene los datos de los jugadores del Atlético de Madrid con todas sus estadísticas.
    
    Returns:
        DataFrame: Datos de los jugadores del Atlético de Madrid
    """
    conn = get_connection()
    if not conn:
        st.error("No se pudo establecer conexión con la base de datos")
        return pd.DataFrame()
    
    try:
        # Primero obtener el ID del equipo Atlético
        query_equipo = "SELECT id_equipo FROM equipos WHERE nombre LIKE '%Atl%' LIMIT 1"
        cursor = conn.cursor()
        cursor.execute(query_equipo)
        equipo_id = cursor.fetchone()[0]
        
        # Consulta principal usando parámetros directamente (más seguro)
        query = """
        SELECT 
            j.nombre AS Jugador,
            j.nacionalidad AS Nacionalidad,
            j.posicion AS Posición,
            j.edad AS Edad,
            j.fecha_nacimiento AS Nacimiento,
            ej.minutos AS Minutos,
            ej.partidos_jugados AS Partidos,
            ej.titularidades AS Titularidades,
            ej.porcentaje_min_equipo AS "% Minutos equipo",
            eo.goles AS Goles,
            eo.goles_sin_penales AS "Goles sin penales",
            eo.asistencias AS Asistencias,
            eo.goles_asistencias AS "Goles+Asistencias",
            eo.xG AS xG,
            eo.xA AS xA,
            eo.xAG AS xAG,
            eo.npxG AS npxG,
            eo.npxG_xAG AS "npxG+xA",
            eo.tiros AS Tiros,
            eo.tiros_puerta AS "Tiros a puerta",
            eo.tiros_por_90 AS "Tiros por 90",
            ep.pases_clave AS "Pases clave",
            ep.porcentaje_pases_completados AS "% Pases completados",
            ep.pases_ultimo_tercio AS "Pases último tercio",
            ep.pases_area_penal AS "Pases al área",
            ep.pases_centros AS "Centros",
            ep.pases_progresivos AS "Pases progresivos",
            epos.toques AS Toques,
            epos.regates_exitosos AS "Regates completados",
            epos.porcentaje_regate AS "% Regate exitoso",
            epos.conducciones_progresivas AS "Conducciones progresivas",
            epos.controles_errados AS "Controles errados",
            epos.desposesiones AS Desposesiones,
            ed.entradas AS Entradas,
            ed.intercepciones AS Intercepciones,
            ed.entradas_intercepciones AS "Entradas+Intercepciones",
            ed.despejes AS Despejes,
            ed.bloqueos AS Bloqueos,
            ed.tackles_ganados AS "Duelos ganados",
            ed.recuperaciones AS Recuperaciones,
            ed.porcentaje_duelos_aereos AS "% Duelos aéreos",
            edis.tarjetas_amarillas AS "Tarjetas amarillas",
            edis.tarjetas_rojas AS "Tarjetas rojas",
            edis.faltas_cometidas AS "Faltas cometidas",
            edis.faltas_recibidas AS "Faltas recibidas",
            edis.fueras_juego AS "Fueras de juego"
        FROM jugadores j
        JOIN estadisticas_jugador ej ON j.id_jugador = ej.id_jugador
        JOIN estadisticas_ofensivas eo ON ej.id_estadistica = eo.id_estadistica
        JOIN estadisticas_pases ep ON ej.id_estadistica = ep.id_estadistica
        JOIN estadisticas_posesion epos ON ej.id_estadistica = epos.id_estadistica
        JOIN estadisticas_defensivas ed ON ej.id_estadistica = ed.id_estadistica
        JOIN estadisticas_disciplina edis ON ej.id_estadistica = edis.id_estadistica
        WHERE ej.id_equipo = ? 
        AND ej.temporada = '2024-2025'
        ORDER BY ej.minutos DESC
        """
        
        player_data = pd.read_sql(query, conn, params=(equipo_id,))
        conn.close()
        # Formatear datos numéricos antes de devolverlos
        return format_player_data(player_data)
    except Exception as e:
        st.error(f"Error en consulta: {str(e)}")
        conn.close()
        return pd.DataFrame()
    
def format_player_data(player_data):
    """
    Formatea los datos numéricos del DataFrame para mejor visualización.
    
    Args:
        player_data (DataFrame): DataFrame con datos de jugadores
        
    Returns:
        DataFrame: DataFrame con valores numéricos formateados
    """
    # Crear una copia para no modificar el original
    formatted_data = player_data.copy()
    
    # Columnas que deben ser texto (no formatear)
    text_columns = ["Jugador", "Nacionalidad", "Posición", "Nacimiento"]
    
    # Columnas con 2 decimales
    decimal_columns = [
        "xG", "xA", "xAG", "npxG", "npxG+xA", "Tiros por 90",
        "% Minutos equipo", "% Pases completados", "% Regate exitoso", "% Duelos aéreos"
    ]
    
    # Formatear cada columna
    for col in formatted_data.columns:
        if col not in text_columns:
            if col in decimal_columns:
                # Redondear a 2 decimales
                formatted_data[col] = pd.to_numeric(formatted_data[col], errors='coerce')
                formatted_data[col] = formatted_data[col].apply(
                    lambda x: round(x, 2) if pd.notnull(x) else x
                )
            else:
                # Convertir a entero
                formatted_data[col] = pd.to_numeric(formatted_data[col], errors='coerce')
                formatted_data[col] = formatted_data[col].apply(
                    lambda x: int(x) if pd.notnull(x) else x
                )
    
    return formatted_data

def get_team_by_id(team_id):
    """
    Obtiene el nombre de un equipo por su ID.
    
    Args:
        team_id (int): ID del equipo
        
    Returns:
        str: Nombre del equipo
    """
    conn = get_connection()
    if not conn:
        return ""
    
    query = "SELECT nombre FROM equipos WHERE id_equipo = ?"
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (team_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return ""
    except Exception as e:
        conn.close()
        return ""

def get_available_teams():
    """
    Obtiene la lista de equipos disponibles en la base de datos.
    
    Returns:
        DataFrame: ID y nombre de los equipos
    """
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    query = """
    SELECT id_equipo, nombre
    FROM equipos
    WHERE id_competicion = (SELECT id_competicion FROM equipos WHERE nombre LIKE '%Atlético%' OR nombre LIKE '%Atletico%' LIMIT 1)
    ORDER BY nombre
    """
    
    try:
        teams = pd.read_sql(query, conn)
        conn.close()
        return teams
    except Exception as e:
        conn.close()
        return pd.DataFrame()

def categorize_metrics(columns):
    """
    Categoriza las métricas por tipo para mejor organización.
    
    Args:
        columns (list): Lista de columnas a categorizar
        
    Returns:
        dict: Diccionario con categorías y sus métricas
    """
    categories = {
        "Básicas": ["Jugador", "Nacionalidad", "Posición", "Edad", "Nacimiento", "Minutos", "Partidos", "Titularidades", "% Minutos equipo"],
        "Ataque": ["Goles", "Goles sin penales", "Asistencias", "Goles+Asistencias", "xG", "xA", "xAG", "npxG", "npxG+xA", "Tiros", "Tiros a puerta", "Tiros por 90"],
        "Pases": ["Pases clave", "% Pases completados", "Pases último tercio", "Pases al área", "Centros", "Pases progresivos"],
        "Posesión": ["Toques", "Regates completados", "% Regate exitoso", "Conducciones progresivas", "Controles errados", "Desposesiones"],
        "Defensa": ["Entradas", "Intercepciones", "Entradas+Intercepciones", "Despejes", "Bloqueos", "Duelos ganados", "Recuperaciones", "% Duelos aéreos"],
        "Disciplina": ["Tarjetas amarillas", "Tarjetas rojas", "Faltas cometidas", "Faltas recibidas", "Fueras de juego"]
    }
    
    # Crear diccionario inverso para buscar la categoría de cada columna
    metric_to_category = {}
    for category, metrics in categories.items():
        for metric in metrics:
            metric_to_category[metric] = category
    
    # Clasificar columnas existentes
    categorized = {category: [] for category in categories}
    for col in columns:
        category = metric_to_category.get(col, "Otros")
        if category in categorized:
            categorized[category].append(col)
    
    return categorized
    