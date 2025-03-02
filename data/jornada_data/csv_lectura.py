import pandas as pd
import os
from pathlib import Path

def normalize_team_name(name):
    """Normaliza nombres de equipos para comparación"""
    replacements = {
        " CF": "", "FC ": "", " FC": "", " de ": " ", "RCD ": "", "RC ": "", "CD ": "",
        "UD ": "", "CA ": "", "Real ": "", "Deportivo ": "", "Alavés": "Alaves", "Leganés": "Leganes",
        "Club ": "", "Atlético": "Atletico", "Español": "Espanyol"
    }
    
    result = name
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result.strip().lower()

def load_match_stats(match_id=None, jornada=None, partido=None):
    """
    Carga las estadísticas de los partidos desde el CSV.
    
    Args:
        match_id (str, optional): ID del partido para filtrar
        jornada (int o str, optional): Número de jornada para filtrar
        partido (str, optional): Nombre del partido (ej. "Atletico Madrid-Girona")
        
    Returns:
        pandas.DataFrame: DataFrame con las estadísticas filtradas
    """
    # Ruta al archivo de estadísticas
    file_path = Path("data/FData/stats/match_stats_24_25.csv")
    
    # Verificar que el archivo existe
    if not file_path.exists():
        return None
    
    # Cargar el CSV
    try:
        df = pd.read_csv(file_path)
        
        # Mostrar las columnas disponibles y ejemplos para depuración
        print(f"Columnas en CSV: {df.columns.tolist()}")
        print(f"Ejemplos de partidos: {df['Partido'].unique()[:5]}")
        
        # Filtrar por jornada si se proporciona
        if jornada is not None:
            # Convertir a int si es posible
            if isinstance(jornada, str) and jornada.replace('ª', '').isdigit():
                jornada = int(jornada.replace('ª', ''))
            df = df[df['Jornada'] == jornada]
            print(f"Filtrado por jornada {jornada}, quedan {len(df)} filas")
        
        # Filtrar por partido si se proporciona, con mayor flexibilidad
        if partido is not None:
            # Obtener ambos equipos
            equipos = partido.split('-')
            if len(equipos) != 2:
                print(f"Formato de partido incorrecto: {partido}")
                return df
                
            equipo_local, equipo_visitante = equipos
            
            # Normalizar nombres para comparación
            local_norm = normalize_team_name(equipo_local)
            visitante_norm = normalize_team_name(equipo_visitante)
            
            # Buscar coincidencias
            matches = []
            for p in df['Partido'].unique():
                p_equipos = p.split('-')
                if len(p_equipos) != 2:
                    continue
                    
                p_local, p_visitante = p_equipos
                p_local_norm = normalize_team_name(p_local)
                p_visitante_norm = normalize_team_name(p_visitante)
                
                # Verificar si coinciden en ambas direcciones
                if (p_local_norm == local_norm and p_visitante_norm == visitante_norm) or \
                   (p_local_norm == visitante_norm and p_visitante_norm == local_norm):
                    matches.append(p)
            
            if matches:
                print(f"Partido(s) encontrado(s): {matches}")
                df = df[df['Partido'].isin(matches)]
            else:
                print(f"No se encontró el partido: {partido}")
                print(f"Buscando: '{local_norm}' y '{visitante_norm}'")
                if jornada is not None:
                    print(f"Partidos disponibles en jornada {jornada}: {df['Partido'].unique()}")
        
        return df
    
    except Exception as e:
        print(f"Error al cargar datos CSV: {str(e)}")
        return None

def get_partido_info(match_id):
    """
    Obtiene información de un partido a partir de su ID.
    Esto debería integrarse con tu sistema de mapeo.
    
    Args:
        match_id (str): ID del partido
        
    Returns:
        dict: Información del partido (jornada, partido, etc.)
    """
    # Esta función debería obtener la información desde tu archivo partidos_master.csv
    # Por ahora, es un placeholder que deberás implementar
    try:
        from data.jornada_data.url_mapeo import load_partidos_master
        
        partidos_df = load_partidos_master()
        partido = partidos_df[partidos_df['match_id'] == match_id]
        
        if not partido.empty:
            return {
                'jornada': partido.iloc[0].get('jornada'),
                'partido': partido.iloc[0].get('partido')
            }
    except Exception as e:
        print(f"Error al obtener información del partido: {str(e)}")
    
    return None

def load_partido_stats(jornada, partido):
    """
    Carga las estadísticas de un partido específico.
    
    Args:
        jornada (int): Número de jornada
        partido (str): Nombre del partido (ej. "Atletico Madrid-Girona")
        
    Returns:
        pandas.DataFrame: DataFrame con las estadísticas del partido
    """
    file_path = Path("data/FData/stats/match_stats_24_25.csv")
    
    try:
        df = pd.read_csv(file_path)
        
        # Convertir jornada a int si es necesario
        if isinstance(jornada, str) and jornada.replace('ª', '').isdigit():
            jornada = int(jornada.replace('ª', ''))
        
        # Filtrar por jornada
        df_jornada = df[df['Jornada'] == jornada]
        
        if df_jornada.empty:
            print(f"No hay datos para la jornada {jornada}")
            return None
        
        # Normalizar nombres para una búsqueda más flexible
        def normalize_team_name(name):
            return (name.replace(" CF", "")
                       .replace(" FC", "")
                       .replace(" de ", " ")
                       .strip())
        
        partido_norm = "-".join([normalize_team_name(team) for team in partido.split("-")])
        
        # Buscar partido con nombres normalizados
        match_df = None
        for p in df_jornada['Partido'].unique():
            p_norm = "-".join([normalize_team_name(team) for team in p.split("-")])
            if p_norm == partido_norm:
                match_df = df_jornada[df_jornada['Partido'] == p]
                print(f"Partido encontrado con formato: {p}")
                break
        
        if match_df is None or match_df.empty:
            print(f"No se encontró el partido {partido} en la jornada {jornada}")
        
        return match_df
    except Exception as e:
        print(f"Error al cargar estadísticas del partido: {str(e)}")
        return None