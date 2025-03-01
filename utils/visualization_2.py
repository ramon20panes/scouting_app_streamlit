import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns

def plot_team_metrics(match_stats, local_info, visitante_info):
    """
    Muestra una tabla comparativa de estadísticas entre dos equipos directamente en Streamlit.
    
    Args:
        match_stats (DataFrame): Estadísticas del partido
        local_info (dict): Información del equipo local
        visitante_info (dict): Información del equipo visitante
    """
    # Verificar que tenemos datos
    if match_stats is None or match_stats.empty:
        st.warning("No hay estadísticas disponibles para este partido")
        return
    
    # Filtrar stats para cada equipo
    local_stats = match_stats[match_stats['Equipo'] == local_info['nombre']].iloc[0] if not match_stats[match_stats['Equipo'] == local_info['nombre']].empty else None
    visitante_stats = match_stats[match_stats['Equipo'] == visitante_info['nombre']].iloc[0] if not match_stats[match_stats['Equipo'] == visitante_info['nombre']].empty else None
    
    if local_stats is None or visitante_stats is None:
        st.warning("No se pudieron encontrar estadísticas para ambos equipos")
        return
    
    # Crear columnas para mostrar las métricas
    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    
    # Mostrar resultado
    resultado = local_stats.get('Resultado', 'N/A')
    
    with col1:
        st.subheader(local_info['nombre'])
        try:
            st.image(local_info['ruta_escudo'], width=60)
        except:
            pass
    
    with col2:
        st.subheader(f"Resultado: {resultado}")
    
    with col3:
        st.subheader(visitante_info['nombre'])
        try:
            st.image(visitante_info['ruta_escudo'], width=60)
        except:
            pass
    
    # Métricas a mostrar
    metrics = [
        'Goles', 'Tiros a Puerta', 'Tiros Fuera', 'Tiros Totales', 'Tiros Bloqueados',
        'Tiros Dentro Area', 'Tiros Fuera Area', 'Faltas', 'CÃ³rners', 'Fueras de Juego',
        'PosesiÃ³n', 'Tarjetas Amarillas', 'Tarjetas Rojas', 'Paradas',
        'Pases Totales', 'Pases Completados', 'PrecisiÃ³n de Pases', 'xG', 'Goles Evitados'
    ]
    
    # Crear DataFrame para la tabla comparativa
    table_data = []
    
    for metric in metrics:
        if metric in local_stats and metric in visitante_stats:
            local_value = local_stats[metric]
            visitante_value = visitante_stats[metric]
            
            # Determinar qué equipo tiene mejor valor
            if metric in ['Faltas', 'Tarjetas Amarillas', 'Tarjetas Rojas']:
                local_better = local_value < visitante_value
            else:
                local_better = local_value > visitante_value
            
            # Crear fila para la tabla
            row = {
                'Métrica': metric,
                f"{local_info['nombre']}": local_value,
                f"{visitante_info['nombre']}": visitante_value
            }
            
            table_data.append(row)
    
    # Crear DataFrame
    comparison_df = pd.DataFrame(table_data)
    
    # Función para estilizar la tabla
    def highlight_better(row):
        local_team = local_info['nombre']
        visitante_team = visitante_info['nombre']
        metric = row['Métrica']
        
        if metric in ['Faltas', 'Tarjetas Amarillas', 'Tarjetas Rojas']:
            local_better = row[local_team] < row[visitante_team]
        else:
            local_better = row[local_team] > row[visitante_team]
        
        if local_better:
            return [
                '',
                'background-color: rgba(0, 255, 0, 0.3)',
                'background-color: rgba(255, 0, 0, 0.2)'
            ]
        elif row[local_team] == row[visitante_team]:
            return ['', '', '']
        else:
            return [
                '',
                'background-color: rgba(255, 0, 0, 0.2)',
                'background-color: rgba(0, 255, 0, 0.3)'
            ]
    
    # Aplicar estilo y mostrar tabla
    styled_df = comparison_df.style.apply(highlight_better, axis=1)
    st.table(styled_df)

def plot_passing_network(network_data, team_name, team_color="#003366"):
    """
    Crea una visualización de la red de pases.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Código para dibujar la red de pases
    # ... (aquí iría tu implementación específica)
    
    plt.title(f"Red de pases - {team_name}")
    
    return fig

def plot_xg_comparison(xg_data, local_info, visitante_info):
    """
    Crea una visualización comparativa de xG.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Código para visualizar datos de xG
    # ... (aquí iría tu implementación específica)
    
    plt.title("Comparación de Expected Goals (xG)")
    
    return fig

def plot_match_momentum(momentum_data, local_name, visitante_name):
    """
    Visualiza el momentum del partido a lo largo del tiempo.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Código para visualizar el momentum
    # ... (aquí iría tu implementación específica)
    
    plt.title(f"Dinámica del partido: {local_name} vs {visitante_name}")
    
    return fig

def plot_shot_map(shot_data, team_name, team_color="#003366"):
    """
    Crea un mapa de tiros para un equipo.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Código para crear el mapa de tiros
    # ... (aquí iría tu implementación específica)
    
    plt.title(f"Mapa de tiros - {team_name}")
    
    return fig