import streamlit as st
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
ADMIN_USER = os.getenv('STREAMLIT_USER')
ADMIN_PASSWORD = os.getenv('STREAMLIT_PASSWORD')
def check_auth():
    """Verifica si el usuario está autenticado"""
    # Ya no necesitamos inicializar aquí, session.py lo hace
    return st.session_state.authentication_status

def login():
    """Maneja la autenticación del usuario"""
    # No necesitamos inicializar aquí
    username = st.text_input("Usuario", key="username")
    password = st.text_input("Contraseña", type="password", key="password")
    
    if st.button("Login", key="login_button"):
        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            st.session_state.authentication_status = True
            st.success("¡Bienvenido a la aplicación!", icon="✅")
            import time
            time.sleep(0.5)  # Pequeña pausa para que se vea el mensaje
            st.session_state.redirect_to = "1_Historico"
            st.rerun()  # Usar st.rerun() en lugar de experimental_rerun
        else:
            st.error('Usuario o contraseña incorrectos', icon="🚨")
            
    return st.session_state.authentication_status