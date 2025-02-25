import streamlit as st
from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()
ADMIN_USER = os.getenv('STREAMLIT_USER')
ADMIN_PASSWORD = os.getenv('STREAMLIT_PASSWORD')
SESSION_TIMEOUT = 1800  # 30 minutos en segundos

def check_session_timeout():
    """Verifica si la sesión ha expirado"""
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
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False
    
    username = st.text_input("Usuario", key="username")
    password = st.text_input("Contraseña", type="password", key="password")
    
    if st.button("Login", key="login_button"):
        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            st.session_state.authentication_status = True
            st.session_state.last_activity = datetime.now()  # Inicializar última actividad
            st.success("¡Bienvenido a la aplicación!", icon="✅")
            time.sleep(0.5)
            st.session_state.redirect_to = "1_Stats 24 25"
            st.rerun()
        else:
            st.error('Usuario o contraseña incorrectos', icon="🚨")

def logout():
    """Cierra la sesión del usuario"""
    # Limpiar todos los estados relevantes
    for key in ['authentication_status', 'redirect_to', 'last_activity']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Redireccionar a la página principal
    st.switch_page("Aplic_Direcc_Deport.py")

def check_auth():
    """Verifica autenticación y timeout"""
    if "authentication_status" in st.session_state and st.session_state.authentication_status:
        if check_session_timeout():
            update_last_activity()
            return True
    return False


