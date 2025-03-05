import streamlit as st
import LanusStats as ls  

# Función cacheada para obtener datos de FotMob
@st.cache_data(ttl=3600)  # Caché durante 1 hora
def get_fotmob_data(match_id):
    """
    Función cacheada para obtener datos de FotMob
    
    Args:
        match_id: ID del partido en FotMob
        
    Returns:
        Datos del partido en formato JSON
    """
    try:
        fotmob = ls.FotMob()
        response = fotmob.request_match_details(match_id)
        return response.json()
    except Exception as e:
        st.error(f"Error al obtener datos de FotMob: {str(e)}")
        return None

# Inicializar caché global si no existe
def init_cache():
    """Inicializa la caché global en session_state si no existe"""
    if 'global_cache' not in st.session_state:
        st.session_state.global_cache = {}

# Función genérica para obtener datos cacheados
def get_cached_data(key, fetch_function, *args, **kwargs):
    """
    Función genérica para obtener datos cacheados o recuperarlos si no existen
    
    Args:
        key: Clave única para los datos
        fetch_function: Función para obtener los datos si no están en caché
        *args, **kwargs: Argumentos para pasar a fetch_function
        
    Returns:
        Los datos cacheados o recuperados
    """
    # Asegurar que la caché está inicializada
    init_cache()
    
    # Comprobar si los datos están en caché
    if key in st.session_state.global_cache:
        return st.session_state.global_cache[key]
    
    # Si no están en caché, recuperarlos
    data = fetch_function(*args, **kwargs)
    
    # Guardar en caché
    st.session_state.global_cache[key] = data
    
    return data

# Función para limpiar la caché
def clear_cache(key=None):
    """
    Limpia la caché
    
    Args:
        key: Clave específica a limpiar (None para limpiar toda la caché)
    """
    init_cache()
    
    if key is None:
        st.session_state.global_cache = {}
    elif key in st.session_state.global_cache:
        del st.session_state.global_cache[key]