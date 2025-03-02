import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
from data.jornada_data.csv_lectura import normalize_team_name  # Ajusta la ruta según tu estructura de directorios
from PIL import Image
import io


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

def plot_passing_network(network_data):
    """
    Genera una visualización de la red de pases de un equipo
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Dibujar el campo de fútbol
    draw_pitch(ax)
    
    # Dibujar nodos (jugadores)
    for node in network_data['nodes']:
        ax.scatter(node['x'], node['y'], s=node['size']*100, 
                  color=node['color'], alpha=0.7, 
                  edgecolors='white', linewidths=1)
        
        # Etiquetas de jugadores
        ax.text(node['x'], node['y'] - 2, node['label'], 
               ha='center', va='center', color='white', 
               fontsize=8, fontweight='bold')
    
    # Dibujar aristas (pases)
    for edge in network_data['edges']:
        ax.plot([edge['source_x'], edge['target_x']], 
                [edge['source_y'], edge['target_y']], 
                color=edge['color'], alpha=edge['weight']/10, 
                linewidth=edge['weight'])
    
    # Añadir leyenda y estadísticas
    ax.set_title("Red de Pases", fontsize=14)
    
    # Información adicional en el gráfico
    ax.text(0, -10, f"Pases totales: {len(network_data['edges'])}", 
           ha='left', fontsize=10)
    ax.text(100, -10, f"Precisión: {network_data.get('accuracy', 0):.1f}%", 
           ha='right', fontsize=10)
    
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