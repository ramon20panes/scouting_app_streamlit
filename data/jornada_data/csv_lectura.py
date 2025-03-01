import pandas as pd
import os
from pathlib import Path

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
        
        # Filtrar por jornada si se proporciona
        if jornada is not None:
            # Convertir a int si es posible
            if isinstance(jornada, str) and jornada.isdigit():
                jornada = int(jornada)
            df = df[df['Jornada'] == jornada]
        
        # Filtrar por partido si se proporciona
        if partido is not None:
            df = df[df['Partido'] == partido]
        
        # Si se proporciona match_id, obtener jornada y partido correspondientes
        if match_id is not None and df.empty:
            # Aquí necesitaríamos una forma de mapear match_id a jornada y partido
            # Esta implementación dependerá de cómo tengas organizado tu sistema
            from data.jornada_data.url_mapeo import get_partido_info
            info = get_partido_info(match_id)
            if info and 'Jornada' in info and 'Partido' in info:
                df = load_match_stats(jornada=info['Jornada'], partido=info['Partido'])
        
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
        match_df = df[(df['Jornada'] == jornada) & (df['Partido'] == partido)]
        return match_df
    except Exception as e:
        print(f"Error al cargar estadísticas del partido: {str(e)}")
        return None