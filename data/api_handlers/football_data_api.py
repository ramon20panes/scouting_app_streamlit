import requests
import os
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from pathlib import Path

def load_teams_mapping():
    """
    Carga el mapeo de equipos desde el CSV
    
    Returns:
        dict: Diccionario con el mapeo de nombres y rutas a escudos
    """
    try:
        # Ajusta la ruta según donde esté tu CSV
        csv_path = Path("data/FData/master/equipos_master.csv")
        
        # Intentar diferentes delimitadores
        delimiters = ['\t', ';', '|', ',']
        
        for delimiter in delimiters:
            try:
                # Leer el CSV con el delimitador actual
                df = pd.read_csv(csv_path, sep=delimiter, dtype=str)
                
                # Imprimir información de depuración
                print(f"Leyendo con delimitador: '{delimiter}'")
                print("Columnas en el CSV:", list(df.columns))
                print("Primeras filas:")
                print(df.head())
                
                # Mapeo manual para manejar variaciones de nombres
                manual_name_mapping = {
                    'Villarreal CF': 'Villarreal CF',
                    'Atletico de Madrid': 'Club Atlético de Madrid',
                    'Athletic Club': 'Athletic Club',
                    'Real Madrid CF': 'Real Madrid CF',
                    'Real Sociedad de Fútbol': 'Real Sociedad de Fútbol',
                    'RCD Espanyol de Barcelona': 'RCD Espanyol de Barcelona',
                    'Valencia CF': 'Valencia CF',
                    'FC Barcelona': 'FC Barcelona',
                    # Añade más mapeos según sea necesario
                }
                
                # Crear diccionario de mapeo
                team_mapping = {}
                for _, row in df.iterrows():
                    # Usar la primera columna como nombre del equipo
                    nombre_csv = row.iloc[0]
                    shortname = row.iloc[1].lower()  # Asumiendo que la segunda columna es el shortname
                    logo_path = row.iloc[-1].strip("'")  # Última columna como ruta del logo
                    
                    # Buscar nombre de mapeo manual o usar nombre original
                    api_name = manual_name_mapping.get(nombre_csv, nombre_csv)
                    
                    team_mapping[api_name] = {
                        'original_name': nombre_csv,
                        'shortname': shortname,
                        'logo_path': logo_path
                    }
                
                # Si llegamos aquí, hemos leído el CSV con éxito
                print("Mapeo de equipos creado:")
                for k, v in team_mapping.items():
                    print(f"{k}: {v}")
                
                return team_mapping
            
            except Exception as e:
                print(f"Error al leer con delimitador '{delimiter}': {e}")
        
        # Si ningún delimitador funciona
        print("No se pudo leer el archivo CSV con ningún delimitador conocido")
        return {}
    
    except Exception as e:
        print(f"Error general al cargar el mapeo de equipos: {e}")
        import traceback
        traceback.print_exc()
        return {}

def find_closest_team_name(api_name, team_mapping):
    """
    Encuentra el nombre de equipo más cercano en el mapeo
    
    Args:
        api_name (str): Nombre del equipo desde la API
        team_mapping (dict): Diccionario de mapeo de equipos
    
    Returns:
        str: Nombre del equipo más cercano o el nombre original
    """
    # Primero buscar coincidencia exacta
    if api_name in team_mapping:
        return api_name
    
    # Buscar coincidencias parciales
    for mapped_name, details in team_mapping.items():
        # Comparaciones sin considerar mayúsculas/minúsculas
        if (mapped_name.lower() in api_name.lower() or 
            api_name.lower() in mapped_name.lower() or
            details['original_name'].lower() in api_name.lower() or
            api_name.lower() in details['original_name'].lower()):
            return mapped_name
    
    # Si no se encuentra, devolver el nombre original
    return api_name

def fetch_matches(api_key):
    """
    Obtiene los partidos del Atlético de Madrid desde la API de football-data.org
    
    Args:
        api_key (str): Clave de API para football-data.org
        
    Returns:
        list: Lista de partidos o None si hay un error
    """
    headers = {'X-Auth-Token': api_key}
    url = 'http://api.football-data.org/v4/teams/78/matches'
    
    # Usar caché para evitar llamadas constantes a la API
    @st.cache_data(ttl=3600)  # Cachear por 1 hora
    def _fetch_api_data(url, headers):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json()['matches']
            
            # Código de depuración opcional
            print("Nombres de equipos en la API:")
            for match in matches:
                print(f"Home: {match['homeTeam']['name']}, Away: {match['awayTeam']['name']}")
            
            return matches
        return None
    
    return _fetch_api_data(url, headers)

def process_matches(matches):
    """
    Procesa los datos de partidos para el formato requerido
    
    Args:
        matches (list): Lista de partidos desde la API
        
    Returns:
        pd.DataFrame: DataFrame con los datos procesados
    """
    # Cargar el mapeo de equipos
    team_mapping = load_teams_mapping()
    
    data = []
    cumulative_points = 0
    
    for match in matches:
        # Usar la función find_closest_team_name para mapear nombres
        home_team = find_closest_team_name(match['homeTeam']['name'], team_mapping)
        away_team = find_closest_team_name(match['awayTeam']['name'], team_mapping)

        if match['competition']['name'] == 'Primera Division':
            home_team_name = match['homeTeam']['name']
            is_home = home_team_name == 'Club Atlético de Madrid'
            opponent = match['awayTeam']['name'] if is_home else home_team_name
            
            if match['score']['winner']:
                home_goals = match['score']['fullTime']['home']
                away_goals = match['score']['fullTime']['away']
                
                if is_home:
                    points = 3 if home_goals > away_goals else (1 if home_goals == away_goals else 0)
                    result = 'W' if home_goals > away_goals else ('D' if home_goals == away_goals else 'L')
                    score = f"{home_goals}-{away_goals}"
                else:
                    points = 3 if away_goals > home_goals else (1 if home_goals == away_goals else 0)
                    result = 'W' if away_goals > home_goals else ('D' if home_goals == away_goals else 'L')
                    score = f"{away_goals}-{home_goals}"  # Mostrar primero los goles del Atleti
                
                cumulative_points += points
                
                data.append({
                    'date': datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ'),
                    'opponent': opponent,
                    'location': 'Local' if is_home else 'Visitante',
                    'result': result,
                    'points': points,
                    'cumulative_points': cumulative_points,
                    'score': score
                })
    
    return pd.DataFrame(data)

def transform_dataframe(df):
    """
    Realiza transformaciones adicionales al DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame original
        
    Returns:
        pd.DataFrame: DataFrame transformado
    """
    # Crear copia para no modificar el original
    df_new = df.copy()
    
    # Convertir fecha a solo día
    df_new['date'] = pd.to_datetime(df_new['date']).dt.strftime('%Y-%m-%d')
        
    # Crear columna de jornada
    df_new['jornada'] = range(1, len(df_new) + 1)
    
    # Cargar el mapeo real de equipos
    team_mapping = load_teams_mapping()
    
    # Aplicar el mapeo a los nombres de los oponentes y agregar ruta al escudo
    df_new['opponent_display'] = df_new['opponent'].apply(
        lambda x: find_closest_team_name(x, team_mapping)
    )
    df_new['opponent_logo'] = df_new['opponent_display'].apply(
        lambda x: team_mapping.get(x, {}).get('logo_path', None)
    )
    
    # Reordenar columnas
    df_new = df_new[['jornada', 'date', 'opponent', 'opponent_display', 'opponent_logo', 
                     'location', 'result', 'points', 'cumulative_points', 'score']]
    
    return df_new

def get_atletico_matches(api_key):
    """
    Función principal que combina todas las operaciones para obtener 
    los datos procesados de los partidos del Atlético
    
    Args:
        api_key (str): Clave de API para football-data.org
        
    Returns:
        pd.DataFrame: DataFrame final con todos los datos procesados
    """
    matches = fetch_matches(api_key)
    if matches:
        df = process_matches(matches)
        return transform_dataframe(df)
    return None