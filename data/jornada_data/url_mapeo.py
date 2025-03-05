import pandas as pd
import os
from pathlib import Path

def load_partidos_master():
    """
    Carga el archivo maestro de partidos con IDs y URLs.
    
    Returns:
        pandas.DataFrame: DataFrame con información de partidos
    """
    file_path = Path("data/FData/master/partidos_master.csv")
    
    if not file_path.exists():
        print(f"Archivo no encontrado: {file_path}")
        return pd.DataFrame()
    
    try:
        # Leer el archivo con separador de punto y coma
        df = pd.read_csv(file_path, sep=';')
        return df
    except Exception as e:
        print(f"Error al cargar el archivo maestro de partidos: {str(e)}")
        try:
            # Intentar con tabulaciones
            df = pd.read_csv(file_path, sep='\t')
            return df
        except:
            try:
                # Intentar con comas
                df = pd.read_csv(file_path, sep=',')
                return df
            except:
                # Si todo falla, devolver DataFrame vacío
                return pd.DataFrame()

def load_equipos_master():
    """
    Carga el archivo maestro de equipos con escudos y nombres.
    
    Returns:
        pandas.DataFrame: DataFrame con información de equipos
    """
    file_path = Path("data/FData/master/equipos_master.csv")
    
    if not file_path.exists():
        print(f"Archivo no encontrado: {file_path}")
        return pd.DataFrame()
    
    try:
        # Intentar con diferentes separadores
        for sep in [';', '\t', ',']:
            try:
                df = pd.read_csv(file_path, sep=sep)
                # Si hay más de una columna, probablemente funcionó
                if len(df.columns) > 1:
                    return df
            except:
                continue
        
        # Si ningún separador estándar funcionó, intentar leer línea por línea
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        header = lines[0].strip().split()
        data = []
        for line in lines[1:]:
            # Dividir por espacios, pero preservar texto entre comillas
            import re
            row = re.findall(r'[^"\s]\S*|".+?"', line.strip())
            row = [item.strip('"') for item in row]
            data.append(row)
        
        df = pd.DataFrame(data, columns=header)
        return df
    
    except Exception as e:
        print(f"Error al cargar el archivo maestro de equipos: {e}")
        return pd.DataFrame()

def get_match_urls(match_id):
    """
    Obtiene las URLs asociadas a un ID de partido específico.
    
    Args:
        match_id (str): ID del partido
        
    Returns:
        dict: Diccionario con las URLs del partido
    """
    partidos_df = load_partidos_master()
    
    # Busca por las posibles columnas de ID
    for id_col in ['id_whoscored', 'id_fotmob']:
        if id_col in partidos_df.columns and match_id in partidos_df[id_col].values:
            match_row = partidos_df[partidos_df[id_col] == match_id].iloc[0]
            
            # Construir diccionario con las URLs disponibles
            urls = {}
            if 'url_whoscored' in match_row and pd.notna(match_row['url_whoscored']):
                urls['whoscored_url'] = match_row['url_whoscored']
            if 'url_fbref' in match_row and pd.notna(match_row['url_fbref']):
                urls['fbref_url'] = match_row['url_fbref']
            if 'id_fotmob' in match_row and pd.notna(match_row['id_fotmob']):
                urls['fotmob_id'] = match_row['id_fotmob']
            if 'id_understat' in match_row and pd.notna(match_row['id_understat']):
                urls['understat_id'] = match_row['id_understat']
                
            return urls
    
    return None

def get_match_by_jornada(jornada):
    """
    Obtiene la información de un partido por su jornada.
    
    Args:
        jornada (int o str): Número o etiqueta de jornada
        
    Returns:
        dict: Información del partido
    """
    partidos_df = load_partidos_master()
    
    # Buscar por número de jornada o por formato de jornada
    for jornada_col in ['Jornada', 'formato_jornada']:
        if jornada_col in partidos_df.columns:
            # Convertir jornada a string para comparar con formato_jornada
            jornada_str = str(jornada)
            
            # Si es un número y buscamos en Jornada, intentar matchear con el número
            if jornada_col == 'Jornada' and jornada_str.isdigit():
                jornada_int = int(jornada_str)
                match_row = partidos_df[partidos_df[jornada_col] == jornada_int]
            else:
                # Buscar coincidencias parciales en formato_jornada
                match_row = partidos_df[partidos_df[jornada_col].str.contains(jornada_str, na=False)]
            
            if not match_row.empty:
                return match_row.iloc[0].to_dict()
    
    return None

def get_partido_info(format_jornada):
    """
    Obtiene información detallada de un partido por su formato de jornada.
    
    Args:
        format_jornada (str): Formato de jornada (ej. "5ª ATM-VAL")
        
    Returns:
        dict: Información detallada del partido
    """
    partidos_df = load_partidos_master()
    equipos_df = load_equipos_master()
    
    if 'formato_jornada' not in partidos_df.columns:
        return None
    
    # Buscar el partido por formato_jornada
    partido = partidos_df[partidos_df['formato_jornada'] == format_jornada]
    if partido.empty:
        return None
    
    partido_info = partido.iloc[0].to_dict()
    
    # Añadir información de equipos local y visitante
    local_id = None
    visitante_id = None
    
    # Buscar IDs de equipos usando shortname
    if 'equipo_local' in partido_info and 'shortname' in equipos_df.columns:
        local_name = partido_info['equipo_local']
        local_team = equipos_df[equipos_df['nombre'] == local_name]
        if not local_team.empty:
            local_id = local_team.iloc[0]['id_streamlit']
    
    if 'equipo_visitante' in partido_info and 'shortname' in equipos_df.columns:
        visitante_name = partido_info['equipo_visitante']
        visitante_team = equipos_df[equipos_df['nombre'] == visitante_name]
        if not visitante_team.empty:
            visitante_id = visitante_team.iloc[0]['id_streamlit']
    
    partido_info['local_id'] = local_id
    partido_info['visitante_id'] = visitante_id
    
    return partido_info

def get_available_jornadas():
    """
    Obtiene la lista de jornadas disponibles en formato legible.
    
    Returns:
        list: Lista de strings con formato de jornada
    """
    partidos_df = load_partidos_master()
    
    if 'formato_jornada' in partidos_df.columns:
        return partidos_df['formato_jornada'].tolist()
    elif 'Jornada' in partidos_df.columns:
        return [f"{j}ª Jornada" for j in partidos_df['Jornada'].tolist()]
    
    return []