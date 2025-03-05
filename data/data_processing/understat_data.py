import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import re
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import streamlit as st


# Función para hoja 2_Visualizacion_24_25.py del xG acumulado de la temporada
def get_atletico_data():
    """Función única que extrae todos los datos necesarios y los devuelve en el formato esperado"""
    # Primer conjunto de datos (xG, xGA, etc.)
    link = "https://understat.com/league/La_liga"
    res = requests.get(link)
    soup = BeautifulSoup(res.content, 'lxml')
    scripts = soup.find_all('script')

    strings = scripts[2].string 
    ind_start = strings.index("('")+2 
    ind_end = strings.index("')") 
    json_data = strings[ind_start:ind_end] 
    json_data = json_data.encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)

    df_expcGL = pd.DataFrame(data['143']['history'])
    df_expcGL = df_expcGL[['xG','xGA','npxG','npxGA','xpts','npxGD']]
    
    # Convertir a float para evitar problemas
    df_expcGL['xG'] = df_expcGL['xG'].astype(float)
    df_expcGL['xGA'] = df_expcGL['xGA'].astype(float)
    df_expcGL['npxG'] = df_expcGL['npxG'].astype(float)
    df_expcGL['npxGA'] = df_expcGL['npxGA'].astype(float)
    df_expcGL['xpts'] = df_expcGL['xpts'].astype(float)
    df_expcGL['npxGD'] = df_expcGL['npxGD'].astype(float)
    
    num_matches = len(df_expcGL)
    df_expcGL['Match'] = np.arange(1, num_matches + 1)
    df_expcGL['xGdif'] = df_expcGL['xG'] - df_expcGL['xGA']
    
    # Segundo conjunto de datos (información de partidos)
    link = "https://understat.com/team/Atletico_Madrid/2024"
    res = requests.get(link)
    soup = BeautifulSoup(res.content,'lxml')
    scripts = soup.find_all('script')

    strings = scripts[1].string 
    ind_start = strings.index("('")+2 
    ind_end = strings.index("')") 
    json_data = strings[ind_start:ind_end] 
    json_data = json_data.encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)

    df1 = pd.DataFrame(data)
    df_h = df1['h'].apply(pd.Series)
    df_a = df1['a'].apply(pd.Series)
    
    # Corregir códigos de equipos
    df_h['short_title_corregido'] = df_h['short_title'].copy()
    df_a['short_title_corregido'] = df_a['short_title'].copy()
    
    # Correcciones para Valladolid
    df_h.loc[(df_h['short_title'] == 'VAL') & (df_h['title'] == 'Real Valladolid'), 'short_title_corregido'] = 'RVL'
    df_a.loc[(df_a['short_title'] == 'VAL') & (df_a['title'] == 'Real Valladolid'), 'short_title_corregido'] = 'RVL'
    
    # Correcciones para Rayo Vallecano
    df_h.loc[df_h['title'] == 'Rayo Vallecano', 'short_title_corregido'] = 'RAY'
    df_a.loc[df_a['title'] == 'Rayo Vallecano', 'short_title_corregido'] = 'RAY'
    
    # Crear columna de jornadas
    df1['short_title_h'] = df_h['short_title_corregido']
    df1['short_title_a'] = df_a['short_title_corregido']
    df1 = df1[['short_title_h','short_title_a']]
    df1['final'] = df1['short_title_h']+df1['short_title_a']
    
    # Diccionario de mapeo para nombres de partidos
    match_mapping = {
        'VILATL': 'VIL-ATM', 'ATLGIR': 'ATM-GIR', 'ATLESP': 'ATM-ESP', 'ATHATL': 'ATH-ATM', 'ATLVAL': 'ATM-VAL', 'RAYATL': 'RAY-ATM',
        'CELATL': 'CEL-ATM', 'ATLRMA': 'ATM-RMA', 'SOCATL': 'RSO-ATM', 'ATLLEG': 'ATM-LEG', 'BETATL': 'BET-ATM', 'ATLLPL': 'ATM-LPM',
        'MALATL': 'MLL-ATM', 'ATLALA': 'ATM-ALA', 'RVLATL': 'RVL-ATM', 'ATLSEV': 'ATM-SEV', 'ATLGET': 'ATM-GET', 'BARATL': 'FCB-ATM',
        'ATLOSA': 'ATM-OSA', 'LEGATL': 'LEG-ATM', 'ATLVIL': 'ATM-VIL', 'ATLMAL': 'ATM-MLL', 'RMAATL': 'RMA-ATM', 'ATLCEL': 'ATM-CEL',
        'VALATL': 'VAL-ATM', 'ATLATH': 'ATM-ATH', 'GETATL': 'GET-ATM', 'ATLBAR': 'ATM-FCB', 'ESPATL': 'ESP-ATM', 'SEVATL': 'SEV-ATM',
        'ATLRVL': 'ATM-RVL', 'LPLATL': 'LPM-ATM', 'ATLRAY': 'ATM-RAY', 'ALAATL': 'ALA-ATM', 'ATLSOC': 'ATM-RSO', 'OSAATL': 'OSA-ATM',
        'ATLBET': 'ATM-BET', 'GIRATL': 'GIR-ATM'
    }
    
    # Crear columna de jornada con formato
    df1['jornada'] = ''
    for i, row in df1.iterrows():
        match = row['final']
        match_fixed = match_mapping.get(match, match)
        jornada_match = f"{i+1}ªJ_{match_fixed}"
        df1.at[i, 'jornada'] = jornada_match
    
    return df_expcGL, df1  # Devolvemos ambos DataFrames

# Funciones extracciones mapa de tiro de partidos

def get_shots_data(match_id):
    """
    Obtiene datos de tiros desde Understat para un partido específico
    
    Args:
        match_id (str): ID del partido en Understat
        
    Returns:
        pd.DataFrame: DataFrame con los datos de tiros o None si hay error
    """
    print(f"Intentando obtener datos para match_id: {match_id}")
    url = f'https://understat.com/match/{match_id}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        print(f"Haciendo solicitud a URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Respuesta obtenida. Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error en la respuesta: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Verificar si hay scripts
        scripts = soup.find_all('script')
        print(f"Número de scripts encontrados: {len(scripts)}")
        
        # Buscar shotsData
        shotsData_found = False
        for script in scripts:
            if 'var shotsData' in str(script):
                shotsData_found = True
                print("Script con shotsData encontrado")
                
                # Extraer la cadena JSON usando expresiones regulares
                pattern = r'var shotsData\s*=\s*JSON\.parse\(\'(.*?)\'\)'
                match = re.search(pattern, str(script))
                if match:
                    json_str = match.group(1)
                    # Decodificar la secuencia de escape
                    json_str = bytes(json_str, 'utf-8').decode('unicode_escape')
                    data = json.loads(json_str)
                    
                    shots = []
                    for team in ['h', 'a']:
                        for shot in data[team]:
                            shots.append({
                                'x': float(shot['X']) * 100,
                                'y': float(shot['Y']) * 100,
                                'player': shot['player'],
                                'minute': int(shot['minute']),
                                'result': shot['result'],
                                'xG': float(shot['xG']),
                                'team': 'Local' if team == 'h' else 'Visitante'
                            })
                    
                    print(f"Datos procesados. Número de tiros: {len(shots)}")
                    return pd.DataFrame(shots)
                else:
                    print("No se pudo extraer el JSON con regex")
        
        if not shotsData_found:
            print("No se encontró el script con shotsData")
            
    except Exception as e:
        print(f"Error al obtener datos de Understat: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    return None

def get_shot_map(understat_id):
    """
    Obtiene los datos de tiros separados por equipos local y visitante
    
    Args:
        understat_id (str): ID del partido en Understat
        
    Returns:
        dict: Diccionario con claves 'local' y 'visitante' conteniendo DataFrames
    """
    shots_df = get_shots_data(understat_id)
    
    if shots_df is None or shots_df.empty:
        return None
    
    return {
        'local': shots_df[shots_df['team'] == 'Local'],
        'visitante': shots_df[shots_df['team'] == 'Visitante']
    }