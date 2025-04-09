import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba

import streamlit as st
import seaborn as sns
from data.jornada_data.csv_lectura import normalize_team_name
from utils.cache import get_fotmob_data
from PIL import Image
import io
import traceback
from highlight_text import fig_text
import LanusStats as ls
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
                try:
                    if metric == 'xG':
                        local_value = f"{float(local_value):.2f}" if pd.notna(local_value) and str(local_value).replace('.', '', 1).isdigit() else local_value
                        visitante_value = f"{float(visitante_value):.2f}" if pd.notna(visitante_value) and str(visitante_value).replace('.', '', 1).isdigit() else visitante_value
                    elif metric == 'Precisión de Pases' or metric == 'Posesión':
                        local_value = f"{float(local_value):.2f}%" if pd.notna(local_value) and str(local_value).replace('.', '', 1).isdigit() else local_value
                        visitante_value = f"{float(visitante_value):.2f}%" if pd.notna(visitante_value) and str(visitante_value).replace('.', '', 1).isdigit() else visitante_value
                    else:
                        # Para valores enteros, primero convertimos a float y luego a entero
                        if pd.notna(local_value) and str(local_value).replace('.', '', 1).isdigit():
                            local_value = f"{int(float(local_value))}"
                        if pd.notna(visitante_value) and str(visitante_value).replace('.', '', 1).isdigit():
                            visitante_value = f"{int(float(visitante_value))}"
                except Exception as e:
                    # Si hay error de conversión, dejamos los valores como están
                    print(f"Error al formatear valores para {metric}: {e}")
                
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
        # Convertir a string para evitar problemas de serialización con Arrow
        comparison_df_safe = comparison_df.copy()
        for col in comparison_df_safe.columns:
            comparison_df_safe[col] = comparison_df_safe[col].astype(str)

        # Usar st.dataframe con los datos convertidos a strings
        st.dataframe(
            comparison_df_safe.style.apply(highlight_better, axis=1),
            height=300,  # Altura fijas
            use_container_width=True  # Ocupa todo el ancho disponible
        )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Función para el match momentum del partido

def fotmob_match_momentum_plot_atletico(match_id, save_fig=False, debug=False):
    """
    Implementación del gráfico de momentum para el Atlético de Madrid:
    - Atlético siempre en azul oscuro, rival siempre en rojo
    """
    try:
        # Inicializar FotMob
        if debug:
            print(f"Inicializando FotMob para match_id: {match_id}")
    
        # Colores fijos
        ATLETICO_COLOR = '#172790'  # Color para el Atlético (azul oscuro)
        RIVAL_COLOR = '#e60000'     # Color para el rival (rojo)
    
        # Obtener datos usando la función cacheada
        try:
            response_json = get_fotmob_data(match_id)
            if debug:
                print("Respuesta JSON procesada correctamente")
        except Exception as e:
            raise Exception(f"Error al solicitar datos del partido {match_id}: {str(e)}")
    
        # Obtener nombres de equipos
        try:
            # Intentar obtener nombres de equipos desde la estructura 'general'
            if 'general' in response_json:
                home_team = response_json['general']['homeTeam']['name']
                away_team = response_json['general']['awayTeam']['name']
            # Intentar obtener desde estructura alternativa (match.teams)
            elif 'match' in response_json and 'teams' in response_json['match']:
                home_team = response_json['match']['teams'][0]['name']
                away_team = response_json['match']['teams'][1]['name']
            # Última alternativa si existe 'header'
            elif 'header' in response_json:
                home_team = response_json['header']['teams'][0]['name']
                away_team = response_json['header']['teams'][1]['name']
            else:
                raise Exception("No se pudo encontrar información de equipos en la respuesta JSON")
                
            if debug:
                print(f"Equipos obtenidos: {home_team} vs {away_team}")
        except Exception as e:
            raise Exception(f"Error al obtener nombres de equipos: {str(e)}")
    
        # Verificar qué equipo es el Atlético
        atletico_is_home = any(name in home_team.lower() for name in ['atl', 'atlético', 'atletico'])
        atletico_is_away = any(name in away_team.lower() for name in ['atl', 'atlético', 'atletico'])
    
        if debug:
            print(f"Home team: {home_team}")
            print(f"Away team: {away_team}")
            print(f"Atlético is home: {atletico_is_home}")
            print(f"Atlético is away: {atletico_is_away}")
    
        # Obtener datos de momentum (diferentes rutas en JSON)
        try:
            # Intentar ruta principal
            if 'content' in response_json and 'matchFacts' in response_json['content'] and 'momentum' in response_json['content']['matchFacts']:
                momentum_data = response_json['content']['matchFacts']['momentum']['main']['data']
            # Intentar ruta alternativa
            elif 'momentum' in response_json:
                momentum_data = response_json['momentum']['main']['data']
            # Otra posible ruta
            elif 'stats' in response_json and 'momentum' in response_json['stats']:
                momentum_data = response_json['stats']['momentum']['main']['data']
            else:
                raise Exception("No se encontraron datos de momentum en la respuesta JSON")
                
            momentum_df = pd.DataFrame(momentum_data)
        
            if debug:
                print("\nPrimeros valores del DataFrame:")
                print(momentum_df.head())
                print(f"\nRango de valores: {momentum_df['value'].min()} a {momentum_df['value'].max()}")
        except Exception as e:
            raise Exception(f"El partido {match_id} no tiene datos de momentum: {str(e)}")
    
        # Crear figura base
        fig, ax = plt.subplots(figsize=(12, 5), facecolor='#d4d4d4')
        ax.set_facecolor('#d4d4d4')
    
        # ASIGNACIÓN DE COLORES CORREGIDA:
        # Los valores de arriba corresponden al equipo local
        # Los valores de abajo corresponden al equipo visitante
        colors = []
        for value in momentum_df['value']:
            if value > 0:  # Valores positivos = equipo local
                colors.append(ATLETICO_COLOR if atletico_is_home else RIVAL_COLOR)
            else:  # Valores negativos = equipo visitante
                colors.append(ATLETICO_COLOR if atletico_is_away else RIVAL_COLOR)
    
        # Dibujar barras con colores asignados
        ax.bar(momentum_df['minute'], momentum_df['value'], color=colors)
    
        # Línea vertical para marcar medio tiempo
        ax.axvline(45.5, ls=':', color='#000000')
    
        # Configuración de ejes
        ax.set_xlabel('Minutes', fontsize=14, color="#000000", weight='bold')
        ax.set_xticks(range(0, 91, 15))
        ax.set_xlim(0, 91)
        ax.tick_params(axis='x', colors="#000000", size=8)
        ax.spines['bottom'].set_color('#000000')
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.set_yticks([])
        
        # ASIGNACIÓN DE COLORES PARA TÍTULO
        home_color = ATLETICO_COLOR if atletico_is_home else RIVAL_COLOR
        away_color = ATLETICO_COLOR if atletico_is_away else RIVAL_COLOR
    
        # Título
        plt.figtext(0.35, 0.87, home_team, color=home_color, fontsize=18, weight='bold', ha='right')
        plt.figtext(0.65, 0.87, away_team, color=away_color, fontsize=18, weight='bold', ha='left')
        
        # if save_fig:
        #    plt.savefig(f'{match_id}_match_momentum.png', bbox_inches='tight')
    
        return fig, ax
    except Exception as e:

        # Capturar cualquier error en la función completa
        print(f"Error completo en fotmob_match_momentum_plot_atletico: {str(e)}")
        print(traceback.format_exc())
        raise e
    
# ----------------------------------------------------------------
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
                               passes_df=None, home_team=None, away_team=None, team_color=None, jornada=None):
    # Definir colores base
    atleti_color = '#172790'  # Azul oscuro para el Atlético de Madrid
    rival_color = '#e60000'   # Rojo para el equipo rival
    bg_color = '#E6E6E6'      # Gris mediano para el fondo del campo
    line_color = '#001F3F'    # Azul oscuro para las líneas y textos
    
    # Usar el color proporcionado o un valor predeterminado
    if team_color is None:
        team_color = atleti_color  # Color predeterminado si no se proporciona
    
    # Corrección específica para jornada 26
    is_atleti = False
    if jornada == "26ª":
        # Chequeo explícito para Atlético vs Athletic
        is_atleti = "Atletico" in teamName or "Atlético" in teamName
        is_home_team = "Atletico" in teamName or "Atlético" in teamName
    else:
        # Determinar si es el equipo local o visitante
        is_home_team = teamName == home_team
        # Determinar si es Atlético
        is_atleti = "Atletico" in teamName or "Atlético" in teamName

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
                          color=bg_color, edgecolor=line_color, linewidth=1, alpha=1, ax=ax)
        else:
            pitch.scatter(row['pass_avg_x'], row['pass_avg_y'], s=1000, marker='s', 
                          color=bg_color, edgecolor=line_color, linewidth=1, alpha=0.75, ax=ax)

    # Plot de los nombres
    for index, row in average_locs_and_count_df.iterrows():
        player_name = row["name"].split()[-1]
        pitch.annotate(player_name, xy=(row.pass_avg_x, row.pass_avg_y), c=team_color, 
                       ha='center', va='center', size=10, weight='bold', ax=ax)

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
        ax.text(avgph-1, -5, f"Altura media:{avgph}m", fontsize=15, color="#000000", ha='right')
        ax.text(105, -5, f"Verticalidad: {verticality}%", fontsize=15, color="#000000", ha='right')
        ax.text(2, 66, "Círculo = Tit\nCuadrado = Sup", color=team_color, size=12, ha='left', va='top')
        ax.set_title(f"{teamName}", color="#000000", size=25, fontweight='bold')
    else:
        # Para visitante (siempre a la derecha), invertir los ejes
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.text(avgph-1, 73, f"Altura media:{avgph}m", fontsize=15, color="#000000", ha='left')
        ax.text(105, 73, f"Verticalidad: {verticality}%", fontsize=15, color="#000000", ha='left')
        ax.text(2, 2, "Círculo = Tit\nCuadrado = Sup", color=team_color, size=12, ha='right', va='top')
        ax.set_title(f"{teamName}", color="#000000", size=25, fontweight='bold')

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

def plot_xg_timeline(df_xG):
    """
    Genera un gráfico de línea de xG acumulado por equipos.
    
    Args:
        df_xG (pd.DataFrame): DataFrame con columnas de xG por equipo
    
    Returns:
        matplotlib.figure.Figure: Figura con el gráfico de xG
    """
    # Configurar el estilo del fondo
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('lightgrey')
    ax.set_facecolor('lightgrey')

    # Identificamos automáticamente los equipos desde los datos
    equipos = df_xG['Equipo'].unique()

     # Verificar que tenemos datos
    if len(equipos) < 1:
        ax.text(0.5, 0.5, "No hay datos de xG disponibles", 
                ha='center', va='center', fontsize=14, color='black')
        return fig

    # Identificar al Atlético (independientemente de su nombre exacto)
    posibles_nombres_atletico = ['atletico', 'atlético', 'atl madrid', 'atl. madrid', 'atletico madrid', 'atlético madrid', 'atlético de madrid']
    atletico_nombre = None

    for equipo in equipos:
        if any(nombre in equipo.lower() for nombre in posibles_nombres_atletico):
            atletico_nombre = equipo
            break

    # Si no se encuentra, usar el primer equipo
    if not atletico_nombre and len(equipos) >= 1:
        atletico_nombre = equipos[0]

    # Identificar al rival (el equipo que no es el Atlético)
    rival_nombre = next((equipo for equipo in equipos if equipo != atletico_nombre), "Rival")

    # Definir colores (Atlético siempre en azul, rival siempre en rojo)
    atleti_color = 'darkblue'
    other_team_color = 'red'

    # Determinar local y visitante basándonos en el dataset
    # Intentemos determinar quién es local y visitante
    equipo_local = None
    equipo_visitante = None
    
    # Buscar en los eventos para detectar quién es local y visitante
    local_rows = df_xG[df_xG['Local'] == True] if 'Local' in df_xG.columns else pd.DataFrame()
    if not local_rows.empty:
        # Tenemos información directa de local/visitante
        equipo_local = local_rows['Equipo'].iloc[0]
        equipo_visitante = next((eq for eq in equipos if eq != equipo_local), "Visitante")
    elif len(equipos) >= 2:
        # Adivinamos basándonos en el orden: primero se suele listar al local
        equipo_local = equipos[0]
        equipo_visitante = equipos[1]
    else:
        # Si no podemos determinar, usamos Atlético y Rival
        equipo_local = atletico_nombre or "Local"
        equipo_visitante = rival_nombre or "Visitante"

    # Ploteamos el xG
    for team in equipos:
        team_df = df_xG[df_xG['Equipo'] == team]
        
        # Agregamos una fila de 0 xG al inicio del partido
        team_df = pd.concat([pd.DataFrame({'Equipo': team, 'Minute': 0, 'xG': 0, 'Resultado': 'Gol', 'cumulative_xG': 0, 'half': 1}, index=[0]), team_df])
        
        # También agregamos una fila al comienzo de la segunda mitad
        first_half_xg = team_df[team_df['half'] == 1]['cumulative_xG'].iloc[-1] if not team_df[team_df['half'] == 1].empty else 0
        team_df = pd.concat([
            team_df[team_df['half'] == 1], 
            pd.DataFrame({'Equipo': team, 'Minute': 45, 'xG': 0, 'Resultado': 'Gol', 'cumulative_xG': first_half_xg, 'half': 2}, index=[0]), 
            team_df[team_df['half'] == 2]
        ])
        
        for half in team_df['half'].unique():
            half_df = team_df[team_df['half'] == half]
            # Asignar color basado en el equipo, no en local/visitante
            team_color = atleti_color if team == atletico_nombre else other_team_color
            ax.plot(
                half_df['Minute'], 
                half_df['cumulative_xG'], 
                label=team, 
                drawstyle='steps-post',
                c=team_color,
                linewidth=1.5
            )   
            
    # Añadimos un scatter para los goles
    for team in equipos:
        team_df = df_xG[(df_xG['Equipo'] == team) & (df_xG['Resultado'] == 'Gol')].to_dict(orient='records')
        for x in team_df:
            # Asignar color basado en el equipo, no en local/visitante
            team_color = atleti_color if team == atletico_nombre else other_team_color
            ax.scatter(
                x['Minute'], 
                x['cumulative_xG'], 
                c='white',
                edgecolor=team_color,
                s=80,
                # Posicionamos en el tope de las líneas
                zorder=5
            )
            
            # Incluimos el nombre del goleador
            ax.text(
                x['Minute'], 
                x['cumulative_xG'] - .07, 
                x['Jugador'], 
                ha='center', 
                va='center',
                weight='bold',
                color='black', 
                fontsize=7,
                zorder=10
            )
            
    # Diferenciamos primera de segunda mitad
    ax.set_xticks([0, 45, 90])
    ax.set_xticklabels(['0\'', '45\'', '90\''], color='#000000')
    # Agregamos Primera y Segunda parte
    ax.text(22.5, -.25, 'Primer tiempo', ha='center',  fontsize=10, weight='bold', color='#000000')
    ax.text(67.5, -.25, 'Segundo tiempo', ha='center',  fontsize=10, weight='bold', color='#000000')
    # Etiquetamos el acumulado
    ax.set_ylabel('xG Acumulado',  fontsize=10, weight='bold', color='#000000')
    
    # Quitamos las barras de arriba y de derecha
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # Cambiamos el color de las spines (ejes izquierdo e inferior)
    ax.spines['left'].set_color('#000000')
    ax.spines['left'].set_linewidth(0.8)  
    ax.spines['bottom'].set_color('#000000')
    ax.spines['bottom'].set_linewidth(0.8)
    # Cambiamos el color de los números en los ejes X e Y
    ax.tick_params(axis='x', colors='#000000', labelsize=8)  # Color de los números del eje X
    ax.tick_params(axis='y', colors='#000000', labelsize=8)  # Color de los números del eje Y

    # Cambiamos el color de los textos en el título
    # Nota: Coloreamos los equipos por su identidad, no por local/visitante
    equipo_local_color = atleti_color if equipo_local == atletico_nombre else other_team_color
    equipo_visitante_color = atleti_color if equipo_visitante == atletico_nombre else other_team_color

    fig_text(
        0.5,
        0.95,
        f'<{equipo_local}> vs <{equipo_visitante}>', 
        fontsize=14, 
        ha='center', 
        va='center', 
        ax=ax,      
        highlight_textprops=[{'color': equipo_local_color}, {'color': equipo_visitante_color}],
        color='#4a4a4a',
        weight='bold'
    )

    plt.tight_layout()
    return fig

def preprocess_xg_data(df_input):
    """
    Preprocesa los datos de xG para su visualización.
    
    Args:
        df_input (pd.DataFrame): DataFrame original de fbref
    
    Returns:
        pd.DataFrame: DataFrame procesado para visualización de xG
    """
    # Seleccionamos las columnas del primer apartado llamado 'ACT', 'GCA' en inglés
    df_processed = df_input.drop(columns=[x for x in df_input.columns if 'ACT' in x[0]])

    # Eliminar nivel superior si hay MultiIndex
    if isinstance(df_processed.columns, pd.MultiIndex):
        df_processed.columns = df_processed.columns.droplevel(0)

    # Verificar que las columnas necesarias existen
    required_cols = ['Equipo', 'Jugador', 'Minute', 'xG', 'Resultado']
    missing_cols = [col for col in required_cols if col not in df_processed.columns]
    if missing_cols:
        raise ValueError(f"Faltan columnas necesarias en el DataFrame: {missing_cols}")

    # Filtrar las columnas necesarias
    df_processed = df_processed[required_cols]

    # Se crea una columna del acumulado
    df_processed['cumulative_xG'] = df_processed.groupby('Equipo')['xG'].cumsum()

    # Se eliminan filas con minutos nulos
    df_processed = df_processed.dropna(subset=['Minute'])

    # Manejar diferentes formatos de minutos
    def parse_minute(minute_value):
        # Si es un número (float o int), simplemente convertirlo a int
        if isinstance(minute_value, (int, float)):
            return 2 if int(minute_value) > 45 else 1, int(minute_value)
        
        # Si es una cadena, intentar procesarla
        try:
            # Manejar formato "45+2" o similar
            if '+' in str(minute_value):
                parts = str(minute_value).split('+')
                base_minute = int(parts[0])
                extra_minute = int(parts[1])
                total_minute = base_minute + extra_minute
            else:
                # Si no tiene "+", convertir directamente
                total_minute = int(minute_value)
                
            # Determinar mitad
            half = 2 if total_minute > 45 else 1
            return half, total_minute
        except Exception as e:
            # En caso de error, asumir primera mitad y minuto 1
            print(f"Error procesando minuto '{minute_value}': {str(e)}")
            return 1, 1

    # Aplicar la función de procesamiento de minutos
    df_processed['half'], df_processed['Minute_processed'] = zip(*df_processed['Minute'].apply(parse_minute))
    
    # Reemplazar la columna original
    df_processed['Minute'] = df_processed['Minute_processed']
    df_processed.drop(columns=['Minute_processed'], inplace=True)

    return df_processed

# ----------------------------------------------------------------
# Representación de tiros de ambos equipos

def plot_shot_map(shots_df, team_name, team_color=None):
    """
    Crea un mapa de tiros para un equipo
    
    Args:
        shots_df (pd.DataFrame): DataFrame con los datos de tiros
        team_name (str): Nombre del equipo
        team_color (str, optional): Color para representar los tiros. Por defecto es None.
        
    Returns:
        matplotlib.figure.Figure: Figura con el mapa de tiros
    """
    if shots_df is None or shots_df.empty:
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, "No hay datos de tiros disponibles", ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    # Determinar si es el Atlético de Madrid para establecer colores
    is_atleti = any(name in team_name.lower() for name in ['atl', 'atlético', 'atletico'])
    
    # Configurar colores
    if team_color is None:
        team_color = '#172790' if is_atleti else '#e60000'  # Azul para Atleti, rojo para rival
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='#F0F0F0')
    
    # Configurar campo
    pitch = Pitch(pitch_type='opta', pitch_length=100, pitch_width=100,
                 pitch_color='#FFFFFF', line_color='#333333', stripe=True,
                 stripe_color='#F8F8F8', half=True)
    
    pitch.draw(ax=ax)
    
    # Dibujar tiros
    for _, shot in shots_df.iterrows():
        is_goal = shot['result'] == 'Goal'
        size = shot['xG'] * 1000  # Tamaño basado en xG
        
        ax.scatter(
            shot['x'],
            shot['y'],
            c=team_color,
            s=size,
            alpha=0.7,
            edgecolors='black',
            linewidth=1 if is_goal else 0.5,
            marker='*' if is_goal else 'o'
        )
    
    # Título y estadísticas
    ax.set_title(f"{team_name}", color='#333333', fontsize=10, weight='bold')
    
    # Leyenda
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=team_color, 
                  markersize=6, label='Tiro'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor=team_color, 
                  markersize=9, label='Gol')
    ]
    ax.legend(handles=legend_elements, loc='upper center', frameon=True, fontsize=8)
    
    # Estadísticas
    stats_text = (f"Tiros: {len(shots_df)} | "
                 f"Goles: {len(shots_df[shots_df['result'] == 'Goal'])} | "
                 f"xG Total: {shots_df['xG'].sum():.2f}")
    
    plt.figtext(0.5, 0.02, stats_text, ha='center', color='#333333', weight='bold', fontsize=8)
    
    plt.tight_layout(pad=0.5)
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