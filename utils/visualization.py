import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplsoccer
from mplsoccer import Bumpy
import highlight_text
from pathlib import Path
import highlight_text
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path

# Definir función para crear un gráfico bumpy chart
def create_bumpy_chart(df, highlight_teams=None):
    """
    Crea un gráfico bumpy chart para visualizar la evolución de posiciones de equipos en La Liga.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de posiciones
        highlight_teams (list): Lista de equipos a destacar
        
    Returns:
        fig, ax: Figura y ejes de matplotlib
    """
    # Equipos por defecto
    if highlight_teams is None or len(highlight_teams) == 0:
        highlight_teams = ["Club Atlético de Madrid", "Real Madrid CF", "FC Barcelona"]
    
    # Paleta de colores para equipos
    team_colors = {
        "Club Atlético de Madrid": "darkblue",
        "Real Madrid CF": "white",
        "FC Barcelona": "#CB3524",
        "Athletic Club": "#282828",
        "Villarreal CF": "#FFD700",
        "Real Betis BalompiÃ©": "#00A650",
        "Sevilla FC": "#C41E3A",
        "Valencia CF": "#FF7500",
        "Real Sociedad de FÃºtbol": "#0066CC",
        "Girona FC": "#C91C2E",
        "CA Osasuna": "#AB1311",        
        "CD Leganés": "#2C3D98",       
        "Deportivo Alavés": "#0067B1",  
        "Getafe CF": "#005999",         
        "RC Celta de Vigo": "#8AD2F0",  
        "RCD Espanyol de Barcelona": "#0070B2", 
        "RCD Mallorca": "#E10D2B",      
        "Rayo Vallecano de Madrid": "#E53027", 
        "Real Valladolid CF": "#6A256F", 
        "UD Las Palmas": "#FFD700"      
    }
    
    # Crear un diccionario de colores solo para los equipos
    highlight_dict = {team: team_colors.get(team, "#A0A0A0") for team in highlight_teams}
    
    # Determinar la última jornada con datos diferentes
    ultima_jornada = None
    for i in range(1, 39):
        columna = f'J{i}'
        if columna in df.columns:
            # Comparar con la columna anterior si existe
            if i > 1 and (df[f'J{i}'] == df[f'J{i-1}']).all():
                ultima_jornada = i-1
                break
        else:
            ultima_jornada = i-1
            break

    if not ultima_jornada:
        ultima_jornada = 38
    
    # Filtrar el DataFrame
    df_filtered = df.iloc[:, :ultima_jornada+1]  # +1 para incluir la columna "Equipo"
    
    # Transponer el dataframe para el formato que necesita el gráfico
    df_plot = df_filtered.set_index('Equipo').T

    # Invertir las posiciones para que 1 esté arriba y 20 abajo
    df_plot = df_plot.applymap(lambda x: 21 - x)  
    
    # Crear las etiquetas de jornadas
    Jornada_labels = ['Jornada ' + str(num) for num in range(1, len(df_plot)+1)]
    
    # Configurar el objeto Bumpy
    bumpy = Bumpy(
        scatter_color='#A0A0A0', 
        line_color='#A0A0A0',
        rotate_xticks=90,
        ticklabel_size=12,
        scatter_primary='D',
        show_right=True,
        plot_labels=True,
        alignment_yvalue=0.1,
        alignment_xvalue=0.065
    )
    
    # Crear el gráfico
    fig, ax = bumpy.plot(
        x_list=Jornada_labels,
        y_list=np.linspace(1, 20, 20).astype(int),
        values=df_plot,
        secondary_alpha=0.3,
        highlight_dict=highlight_dict,
        figsize=(12, 6),  
        y_label='Posición',
        x_label='Jornadas',
        ylim=(20.5, 0.5),
        lw=2
    )
    # Cambiar el color de la etiqueta 'Posición' a darkblue
    ax.set_ylabel('Posición', color='darkblue', fontweight='bold')
    ax.set_xlabel('Jornadas', color='darkblue', fontweight='bold')

    # Configurar etiquetas de eje X (jornadas)
    ax.set_xticks(range(len(Jornada_labels)))
    ax.set_xticklabels([f"J{i+1}" for i in range(len(Jornada_labels))], rotation=90, color="darkblue", weight='bold')

    # Configurar etiquetas de eje Y (posiciones)
    ax.set_yticks(range(1, 21))
    ax.set_yticklabels([str(i) for i in range(1, 21)], color="darkblue", weight='bold')
    
    # Configurar estilo del gráfico
    ax.set_facecolor('#d4d4d4')
    fig.patch.set_facecolor('#d4d4d4')
    
    # Actualizar título a negro
    fig.text(
        s='Progresión Clasificación LaLiga 24/25',
        x=.5, 
        y=.95,
        c='black',  
        size=18,
        weight='bold',
        ha='center'
    )
    
    # Texto con equipos
    highlight_text_str = ""
    highlight_textprops = []
    
    for i, team in enumerate(highlight_teams):
        if i > 0:
            highlight_text_str += ", "
        highlight_text_str += f"<{team}>"
        highlight_textprops.append({"color": highlight_dict[team]})
    
    highlight_text.fig_text(
        x=.5, 
        y=.93,
        s=highlight_text_str,
        highlight_textprops=highlight_textprops,
        fontsize=14,
        color='black',  
        ha='center'
    )
    
    # Añadir logos
        
    # Escudo del Atleti
    ax2 = fig.add_axes([0.02, 0.92, 0.1, 0.1])
    ax2.axis('off')
    try:
        img_atleti = Image.open('assets/escudos/atm.png')
        ax2.imshow(img_atleti)
    except Exception as e:
        print(f"No se pudo cargar el escudo del Atleti: {str(e)}")
    
    # Logo de LaLiga
    ax3 = fig.add_axes([0.90, 0.92, 0.1, 0.1])
    ax3.axis('off')
    try:
        img_laliga = Image.open('assets/logos/laliga.png')
        ax3.imshow(img_laliga)
    except Exception as e:
        print(f"No se pudo cargar el logo de LaLiga: {str(e)}")
    
    return fig, ax

# ----------------------------------------------------------------
# Códigos para el gráfico Timeline de los resultados del atleti en la liga

def get_team_logo(team_name, team_mapping, default_scale=0.08):
    """
    Obtiene el logo de un equipo con escalado personalizado
    
    Args:
        team_name (str): Nombre del equipo
        team_mapping (dict): Diccionario de mapeo de equipos
        default_scale (float): Escala por defecto
    
    Returns:
        OffsetImage: Imagen del logo escalada o None si no se encuentra
    """
    # Mapeo específico para nombres problemáticos
    name_mapping = {
        'Barcelona': 'FC Barcelona',
        'Leganés': 'CD Leganes',
        'CD Leganés': 'CD Leganes',
        'Alavés': 'Deportivo Alaves',
        'Deportivo Alavés': 'Deportivo Alaves',
        'Real Madrid CF': 'Real Madrid',
        'Real Sociedad de Fútbol': 'Real Sociedad',
        'RCD Espanyol de Barcelona': 'RCD Español',
        'RCD Espanyol': 'RCD Español',
        'Espanyol': 'RCD Español',
        'Las Palmas': 'UD Las Palmas',
        'Real Valladolid CF': 'Real Valladolid',
        'Rayo Vallecano de Madrid': 'Rayo Vallecano',
    }
    
    # Buscar en el mapeo de nombres
    if team_name in name_mapping:
        team_name = name_mapping[team_name]
    
    # Diccionario de escalas personalizadas por equipo
    scales = {
        'Girona FC': 0.027,
        'Athletic Club': 0.03,
        'Valencia CF': 0.028,
        'Real Madrid': 0.03,  
        'Real Sociedad': 0.03,  
        'Real Betis': 0.03,
        'FC Barcelona': 0.027,
        'RCD Español': 0.052,
        'Villarreal CF': 0.09,
        'Sevilla FC': 0.06,
        'Rayo Vallecano': 0.06,
        'RC Celta de Vigo': 0.075,
        'CD Leganes': 0.08,
        'UD Las Palmas': 0.136,
        'RCD Mallorca': 0.14,
        'CA Osasuna': 0.1,
        'Deportivo Alaves': 0.1,
        'Real Valladolid': 0.11,
        'Getafe CF': 0.11,
    }
    
    # Obtener la información del equipo del mapeo
    team_info = None
    
    # Buscar coincidencia exacta primero
    if team_name in team_mapping:
        team_info = team_mapping[team_name]
    else:
        # Buscar sin considerar mayúsculas/minúsculas
        for mapped_name, info in team_mapping.items():
            if mapped_name.lower() == team_name.lower():
                team_info = info
                break
    
    # Si aún no se encuentra, buscar coincidencias parciales
    if team_info is None:
        for mapped_name, info in team_mapping.items():
            if mapped_name.lower() in team_name.lower() or team_name.lower() in mapped_name.lower():
                team_info = info
                break
    
    if team_info is None:
        return None
    
    # Obtener la ruta del logo
    logo_path = team_info.get('logo_path', '')
    
    # Eliminar comillas simples si existen
    if logo_path.startswith("'") and logo_path.endswith("'"):
        logo_path = logo_path[1:-1]
    
    # Obtener el zoom
    zoom = scales.get(team_name, default_scale)
    
    try:
        if logo_path:
            # Verificar si la ruta es relativa
            path_obj = Path(logo_path)
            if not path_obj.is_absolute():
                # Buscar en diferentes ubicaciones relativas
                possible_paths = [
                    path_obj,
                    Path("assets/escudos") / path_obj.name,
                    Path("assets") / path_obj,
                    Path("assets/escudos") / Path(logo_path).name
                ]
                
                for p in possible_paths:
                    if p.exists():
                        logo_path = str(p)                        
                        break
            
            if Path(logo_path).exists():
                img = plt.imread(logo_path)
                return OffsetImage(img, zoom=zoom, alpha=1)
            else:
                print(f"❌ No se pudo encontrar el archivo: {logo_path}")
        else:
            print(f"❌ Ruta de logo vacía para {team_name}")
    except Exception as e:
        
        import traceback
        traceback.print_exc()
    
    return None

def create_match_timeline(df, team_mapping):
    """
    Crea un timeline de partidos del Atlético usando matplotlib
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de partidos
        team_mapping (dict): Diccionario de mapeo de equipos
    
    Returns:
        fig: Figura de matplotlib
    """
    # Crear figura y ejes explícitamente
    fig, ax = plt.subplots(figsize=(12, 9), facecolor='#d4d4d4')
    ax.set_facecolor('#d4d4d4')
    #E0E0E0
    # Configuración de colores y barras
    colors = {'W': 'green', 'D': 'orange', 'L': 'red'}
    bar_width = 0.5

    # Dibujar barras y escudos
    for idx, row in df.iterrows():
        height = row['points']
        ax.bar(row['jornada'], height, color=colors[row['result']], alpha=0.7, width=bar_width)
        
        # Añadir barra roja para derrotas
        if row['result'] == 'L':
            ax.vlines(x=row['jornada'], ymin=-0.3, ymax=0, color='red', linewidth=8)

        y_pos = height + 0.1
        
        # Obtener logo con escalado personalizado
        logo = get_team_logo(row['opponent_display'], team_mapping)
        if logo:
            ab = AnnotationBbox(logo, 
                               (row['jornada'], y_pos),
                               frameon=False, 
                               box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
        else:
            # Mostrar texto si no hay logo
            ax.text(row['jornada'], y_pos,
                   row['opponent_display'].split()[-1],
                   ha='center', va='center',
                   fontsize=8, color='black',
                   bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.2'))

        # Para local/visitante
        ax.text(row['jornada'], -1.05,
               'L' if row['location'] == 'Local' else 'V',
               ha='center', va='center',
               fontsize=10,
               weight='bold',
               color='darkblue')

        result_color = colors[row['result']]
        ax.text(row['jornada'], height + 0.6,
               row['score'],
               ha='center',
               va='bottom',
               fontsize=10,
               weight='bold',
               color=result_color)
        
        # Añadir fecha del partido
        ax.text(row['jornada'], -2,
               row['date'],
               ha='center',
               va='center',
               fontsize=8,
               weight='bold',
               color='darkblue',
               rotation=60)

    # Configuraciones adicionales del gráfico
    # Eliminar spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Configurar eje Y - quitar las marcas
    ax.set_yticks([0, 1, 3])
    ax.set_yticklabels(['0', '1', '3'])  # Etiquetas vacías para quitar los números
    ax.tick_params(axis='y', colors='darkblue', size=0)

    # Ajustar eje X para mostrar solo jornadas del 1 al 25
    ax.set_xticks(range(1, 26))
    ax.set_xticklabels(range(1, 26), color='darkblue')
    ax.tick_params(axis='x', colors='darkblue', size=0)

    # Título personalizado
    plt.title('Atlético de Madrid 24/25', 
             color='darkblue', 
             fontsize=18, 
             fontweight='bold', 
             pad=65)  # Aumentar el pad para subir el título

    # Calcular estadísticas
    total_matches = len(df)
    total_points = df['points'].sum()
    wins = len(df[df['result'] == 'W'])
    draws = len(df[df['result'] == 'D'])
    losses = len(df[df['result'] == 'L'])

    # Añadir estadísticas en la parte inferior
    stats_text = (
        f"Partidos disputados: {total_matches}\n"
        f"Puntos totales: {total_points}\n"
        f"Victorias: {wins} | Empates: {draws} | Derrotas: {losses}"
    )

    plt.text(0.9, 1.4, 
             stats_text, 
             horizontalalignment='center',
             verticalalignment='center',
             transform=ax.transAxes,
             color='darkblue',
             fontsize=12)

    plt.tight_layout()
    
    return fig