import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba
import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
from data.jornada_data.csv_lectura import normalize_team_name   # Ajusta la ruta según tu estructura de directorios
from PIL import Image
import io
import traceback

from mplsoccer import Pitch


def plot_team_metrics(match_stats, local_info, visitante_info):
    """
    Muestra una tabla comparativa de estadísticas entre dos equipos directamente en Streamlit.
    """
    # Verificar que tenemos datos
    if match_stats is None or match_stats.empty:
        st.warning("No hay estadísticas disponibles para este partido")
        return
    
    # Configuración de columnas para diseño horizontal
    col1, col2 = st.columns([1, 2])
    
    # Equipos en estadísticas
    equipos_en_stats = match_stats['Equipo'].unique()
    
    def find_team_in_stats(team_info, equipos_disponibles):
        # Intentar con el nombre exacto
        if team_info['nombre'] in equipos_disponibles:
            return team_info['nombre']
    
        # Normalizar nombre
        nombre_norm = normalize_team_name(team_info['nombre'])
    
        # Buscar coincidencia normalizada
        for equipo in equipos_disponibles:
            equipo_norm = normalize_team_name(equipo)
            if nombre_norm == equipo_norm:
                return equipo
    
        # Si no se encuentra, imprimir información de depuración
        print(f"No se encontró coincidencia para: {team_info['nombre']}")
        print(f"Nombre normalizado: {nombre_norm}")
        print(f"Equipos disponibles: {equipos_disponibles}")
    
        return None
    
    # Buscar equipos en estadísticas
    local_name_in_stats = find_team_in_stats(local_info, equipos_en_stats)
    visitante_name_in_stats = find_team_in_stats(visitante_info, equipos_en_stats)
    
    # Si no se encontraron, mostrar mensaje y salir
    if local_name_in_stats is None or visitante_name_in_stats is None:
        st.warning("No se pudieron encontrar estadísticas para ambos equipos")
        st.write(f"Equipos en estadísticas: {equipos_en_stats}")
        st.write(f"Buscando: {local_info['nombre']} y {visitante_info['nombre']}")
        return
    
    # Filtrar stats para cada equipo
    local_stats = match_stats[match_stats['Equipo'] == local_name_in_stats].iloc[0]
    visitante_stats = match_stats[match_stats['Equipo'] == visitante_name_in_stats].iloc[0]

    # Mostrar resultado
    resultado = local_stats.get('Resultado', 'N/A')

    with col1:
        # Contenedor para escudos y resultado
        equipo_row = st.columns([1, 1])
    
        # Escudo local
        with equipo_row[0]:
            st.image(local_info['ruta_escudo'], width=200)  # Tamaño aumentado
    
        # Escudo visitante
        with equipo_row[1]:
            st.image(visitante_info['ruta_escudo'], width=200)  # Tamaño aumentado

        # Resultado centrado
        st.markdown(f"""
        <div style='
            text-align: center; 
            font-size: 48px; 
            font-weight: bold;
            margin-top: 20px;
        '>
            {resultado}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Métricas a mostrar
        metrics = [
            'Goles', 'xG','Precisión de Pases', 'Posesión','Pases Totales', 'Pases Completdos',
            'Tiros a Puerta', 'Tiros Totales', 'Tiros Dentro Area', 'Tiros Fuera Area', 'Goles Evitados',
            'Faltas', 'Tarjetas Amarillas', 'Tarjetas Rojas', 'Fueras de Juego', 'Córners'
        ]
        
        # Crear DataFrame para la tabla comparativa
        table_data = []
        
        for metric in metrics:
            if metric in local_stats and metric in visitante_stats:
                local_value = local_stats[metric]
                visitante_value = visitante_stats[metric]
                
                # Formatear valores: enteros para todo excepto xG y Precisión
                if metric == 'xG':
                    local_value = f"{float(local_value):.2f}" if isinstance(local_value, (int, float)) else local_value
                    visitante_value = f"{float(visitante_value):.2f}" if isinstance(visitante_value, (int, float)) else visitante_value
                elif metric == 'Precisión de Pases' or metric == 'Posesión':
                    local_value = f"{float(local_value):.2f}%" if isinstance(local_value, (int, float)) else local_value
                    visitante_value = f"{float(visitante_value):.2f}%" if isinstance(visitante_value, (int, float)) else visitante_value
                else:
                    local_value = f"{int(float(local_value))}" if isinstance(local_value, (int, float)) else local_value
                    visitante_value = f"{int(float(visitante_value))}" if isinstance(visitante_value, (int, float)) else visitante_value
                
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
            
            # Convertir valores a números para comparación
            try:
                local_val = float(row[local_team].replace('%', '')) if '%' in str(row[local_team]) else float(row[local_team])
                visit_val = float(row[visitante_team].replace('%', '')) if '%' in str(row[visitante_team]) else float(row[visitante_team])
                
                if metric in ['Faltas', 'Tarjetas Amarillas', 'Tarjetas Rojas']:
                    local_better = local_val < visit_val
                else:
                    local_better = local_val > visit_val
                    
                if local_better:
                    return ['', 'background-color: rgba(0, 255, 0, 0.3)', 'background-color: rgba(255, 0, 0, 0.2)']
                elif local_val == visit_val:
                    return ['', '', '']
                else:
                    return ['', 'background-color: rgba(255, 0, 0, 0.2)', 'background-color: rgba(0, 255, 0, 0.3)']
            except:
                # Si hay error en la comparación, no aplicar estilo
                return ['', '', '']
        
        # Usar st.dataframe en lugar de st.table para scroll
        st.dataframe(
            comparison_df.style.apply(highlight_better, axis=1),
            height=300,  # Altura fija
            use_container_width=True  # Ocupa todo el ancho disponible
        )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Función red de pases


# Colores globales
green = '#2d9900'
red = '#e60000'
blue = '#172790'
bg_color = '#f5f5f5'
line_color = '#000000'
atleti_color = '#172790'
rival_color = '#e60000'

def pass_network_visualization(ax, passes_between_df, average_locs_and_count_df, teamName, 
                               passes_df=None, home_team=None, away_team=None, team_color=None):
    # Definir colores base
    atleti_color = '#172790'  # Azul oscuro para el Atlético de Madrid
    rival_color = '#e60000'   # Rojo para el equipo rival
    bg_color = '#E6E6E6'      # Gris mediano para el fondo del campo
    line_color = '#001F3F'    # Azul oscuro para las líneas y textos
    
    # Usar el color proporcionado o un valor predeterminado
    if team_color is None:
        team_color = atleti_color  # Color predeterminado si no se proporciona
    
    # Determinar si es el equipo local o visitante
    is_home_team = teamName == home_team

    MAX_LINE_WIDTH = 15
    passes_between_df['width'] = (passes_between_df.pass_count / passes_between_df.pass_count.max() * MAX_LINE_WIDTH)
    
    MIN_TRANSPARENCY = 0.05
    MAX_TRANSPARENCY = 0.85
    color = np.array(to_rgba(team_color))
    color = np.tile(color, (len(passes_between_df), 1))
    c_transparency = passes_between_df.pass_count / passes_between_df.pass_count.max()
    c_transparency = (c_transparency * (MAX_TRANSPARENCY - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency

    pitch = Pitch(pitch_type='uefa', corner_arcs=True, pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)

    # Plot de las líneas
    pitch.lines(passes_between_df.pass_avg_x, passes_between_df.pass_avg_y, 
                passes_between_df.pass_avg_x_end, passes_between_df.pass_avg_y_end,
                lw=passes_between_df.width, color=color, zorder=1, ax=ax)

    # Plot de los nodos
    for index, row in average_locs_and_count_df.iterrows():
        if row['isFirstEleven'] == True:
            pitch.scatter(row['pass_avg_x'], row['pass_avg_y'], s=1000, marker='o', 
                          color=bg_color, edgecolor=line_color, linewidth=2, alpha=1, ax=ax)
        else:
            pitch.scatter(row['pass_avg_x'], row['pass_avg_y'], s=1000, marker='s', 
                          color=bg_color, edgecolor=line_color, linewidth=2, alpha=0.75, ax=ax)

    # Plot de los nombres
    for index, row in average_locs_and_count_df.iterrows():
        player_name = row["name"].split()[-1]
        pitch.annotate(player_name, xy=(row.pass_avg_x, row.pass_avg_y), c=team_color, 
                       ha='center', va='center', size=9, weight='bold', ax=ax)

    # Linea que marca la altura media de los pases
    avgph = round(average_locs_and_count_df['pass_avg_x'].median(), 2)
    ax.axvline(x=avgph, color='gray', linestyle='--', alpha=0.75, linewidth=2)

    # Altura media de pases de los defensores
    center_backs_height = average_locs_and_count_df[average_locs_and_count_df['position']=='DC']
    def_line_h = round(center_backs_height['pass_avg_x'].median(), 2) if not center_backs_height.empty else avgph
    ax.axvline(x=def_line_h, color='gray', linestyle='dotted', alpha=0.5, linewidth=2)
    
    # Altura media de pases de los dos jugadores más adelantados
    Forwards_height = average_locs_and_count_df[average_locs_and_count_df['isFirstEleven']==1]
    Forwards_height = Forwards_height.sort_values(by='pass_avg_x', ascending=False)
    Forwards_height = Forwards_height.head(2)
    fwd_line_h = round(Forwards_height['pass_avg_x'].mean(), 2) if not Forwards_height.empty else avgph
    ax.axvline(x=fwd_line_h, color='gray', linestyle='dotted', alpha=0.5, linewidth=2)
    
    # Color de la zona media de posiciones del equipo
    ymid = [0, 0, 68, 68]
    xmid = [def_line_h, fwd_line_h, fwd_line_h, def_line_h]
    ax.fill(xmid, ymid, team_color, alpha=0.1)

    # Verticalidad de los equipos
    if passes_df is not None:
        team_passes_df = passes_df[passes_df["teamName"] == teamName].copy()
        team_passes_df['pass_or_carry_angle'] = team_passes_df['pass_or_carry_angle'].abs()
        team_passes_df = team_passes_df[
            (team_passes_df['pass_or_carry_angle']>=0) & 
            (team_passes_df['pass_or_carry_angle']<=90)
        ]
        med_ang = team_passes_df['pass_or_carry_angle'].median()
        verticality = round((1 - med_ang/90)*100, 2)
    else:
        verticality = 0

    # Extrayendo el top de asociaciones de pases
    passes_between_df_sorted = passes_between_df.sort_values(by='pass_count', ascending=False)
    most_pass_from = passes_between_df_sorted['name'].iloc[0] if not passes_between_df_sorted.empty else "N/A"
    most_pass_to = passes_between_df_sorted['name_end'].iloc[0] if not passes_between_df_sorted.empty else "N/A"
    most_pass_count = passes_between_df_sorted['pass_count'].iloc[0] if not passes_between_df_sorted.empty else 0
    
    # Para el equipo local (siempre a la izquierda)
    if is_home_team:
        # No invertir ejes
        ax.text(avgph-1, -5, f"Altura media:{avgph}m", fontsize=15, color=line_color, ha='right')
        ax.text(105, -5, f"Verticalidad: {verticality}%", fontsize=15, color=line_color, ha='right')
        ax.text(2, 66, "Círculo = Tit\nCuadrado = Sup", color=team_color, size=12, ha='left', va='top')
        ax.set_title(f"{teamName}", color=line_color, size=25, fontweight='bold')
    else:
        # Para visitante (siempre a la derecha), invertir los ejes
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.text(avgph-1, 73, f"Altura media:{avgph}m", fontsize=15, color=line_color, ha='left')
        ax.text(105, 73, f"Verticalidad: {verticality}%", fontsize=15, color=line_color, ha='left')
        ax.text(2, 2, "Círculo = Tit\nCuadrado = Sup", color=team_color, size=12, ha='right', va='top')
        ax.set_title(f"{teamName}", color=line_color, size=25, fontweight='bold')

    # Devuelve las estadísticas 
    return {
        'Team_Name': teamName,
        'Defense_Line_Height': def_line_h,
        'Verticality_%': verticality,
        'Most_pass_combination_from': most_pass_from,
        'Most_pass_combination_to': most_pass_to,
        'Most_passes_in_combination': most_pass_count,
    }

    

# ----------------------------------------------------------------
# Función visualización xG comparación

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

def draw_pitch(ax, half=False):
    """Dibuja un campo de fútbol"""
    # Rectángulo del campo
    rect = plt.Rectangle((0, 0), 100, 100, fc='green', alpha=0.3)
    ax.add_patch(rect)
    
    if half:
        # Medio campo
        ax.plot([50, 50], [0, 100], 'white')
        
        # Área grande
        rect = plt.Rectangle((83, 18), 17, 64, fc='none', ec='white')
        ax.add_patch(rect)
        
        # Área pequeña
        rect = plt.Rectangle((94, 36), 6, 28, fc='none', ec='white')
        ax.add_patch(rect)
        
        # Punto de penalti
        ax.scatter(88, 50, color='white', s=10)
        
        # Arco de penalti
        arc = mpatches.Arc((88, 50), 20, 20, theta1=310, theta2=50, ec='white')
        ax.add_patch(arc)
    else:
        # Línea de medio campo
        ax.plot([50, 50], [0, 100], 'white')
        ax.add_patch(plt.Circle((50, 50), 10, fc='none', ec='white'))
        
        # Área grande (izquierda)
        rect = plt.Rectangle((0, 18), 17, 64, fc='none', ec='white')
        ax.add_patch(rect)
        
        # Área grande (derecha)
        rect = plt.Rectangle((83, 18), 17, 64, fc='none', ec='white')
        ax.add_patch(rect)
        
        # Áreas pequeñas
        rect = plt.Rectangle((0, 36), 6, 28, fc='none', ec='white')
        ax.add_patch(rect)
        rect = plt.Rectangle((94, 36), 6, 28, fc='none', ec='white')
        ax.add_patch(rect)
        
        # Puntos de penalti
        ax.scatter(12, 50, color='white', s=10)
        ax.scatter(88, 50, color='white', s=10)
    
    # Remover ejes
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.axis('off')