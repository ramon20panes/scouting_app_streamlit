import streamlit as st
import os
import time
from datetime import datetime, timedelta

# Modificación para manejar credenciales
def get_credentials():
    """
    Obtiene credenciales de variables de entorno locales o secrets de Streamlit
    """
    try:
        # Primero intenta cargar de Streamlit secrets
        ADMIN_USER = st.secrets["STREAMLIT_USER"]
        ADMIN_PASSWORD = st.secrets["STREAMLIT_PASSWORD"]
        print(f"Secrets cargados: User={ADMIN_USER}, Password={'*' * len(ADMIN_PASSWORD)}")
    except:
        print(f"Error al cargar secrets: {e}")
        # Si falla, intenta cargar de variables de entorno locales
        from dotenv import load_dotenv
        load_dotenv()
        ADMIN_USER = os.getenv('STREAMLIT_USER')
        ADMIN_PASSWORD = os.getenv('STREAMLIT_PASSWORD')
        print(f"Env vars cargadas: User={ADMIN_USER}, Password={'*' * len(ADMIN_PASSWORD)}")
    
    return ADMIN_USER, ADMIN_PASSWORD

# El resto de tu código de autenticación permanece igual
def check_session_timeout():
    """Verifica si la sesión ha expirado"""
    SESSION_TIMEOUT = 1800  # Definir aquí también
    
    if 'last_activity' in st.session_state:
        last_activity = st.session_state.last_activity
        if (datetime.now() - last_activity).total_seconds() > SESSION_TIMEOUT:
            # En lugar de llamar a logout aquí, solo limpiamos el estado
            st.session_state.authentication_status = False
            st.session_state.last_activity = None
            return False
    return True      

def update_last_activity():
    """Actualiza el timestamp de última actividad"""
    st.session_state.last_activity = datetime.now()

def login():
    """Maneja la autenticación del usuario"""
    SESSION_TIMEOUT = 1800  # 30 minutos en segundos
    
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False
    
    username = st.text_input("Usuario", key="username")
    password = st.text_input("Contraseña", type="password", key="password")
    
    # Obtener credenciales de manera unificada
    ADMIN_USER, ADMIN_PASSWORD = get_credentials()

    st.write(f"DEBUG: Intentando login con usuario '{username}'")
    
    if st.button("Login", key="login_button"):
        st.write(f"DEBUG: Comparando '{username}' con '{ADMIN_USER}'")
        st.write(f"DEBUG: Comparando password")
        
        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            st.session_state.authentication_status = True
            st.session_state.last_activity = datetime.now()
            st.success("¡Bienvenido a la aplicación!", icon="✅")
            time.sleep(0.5)
            st.session_state.redirect_to = "1_📊Stats 24 25"
            st.rerun()
        else:
            st.error('Usuario o contraseña incorrectos', icon="🚨")

# Resto de las funciones igual que en tu código original
def logout():
    """Cierra la sesión del usuario"""
    for key in ['authentication_status', 'redirect_to', 'last_activity']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.switch_page("Aplic_Direcc_Deport.py")

def check_auth():
    """Verifica autenticación y timeout"""
    if "authentication_status" in st.session_state and st.session_state.authentication_status:
        if check_session_timeout():
            update_last_activity()
            return True
    return False