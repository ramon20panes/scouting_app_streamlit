import streamlit as st
import os

def show_debug_info():
    """Muestra información de depuración"""
    st.header("Información de Depuración")
    
    st.subheader("Secrets")
    try:
        secrets_keys = list(st.secrets.keys())
        st.write("Claves en secrets:", secrets_keys)
    except Exception as e:
        st.error(f"Error al acceder a secrets: {str(e)}")
    
    st.subheader("Variables de Entorno")
    env_vars = {
        "STREAMLIT_USER": os.getenv('STREAMLIT_USER'),
        "STREAMLIT_PASSWORD": "**********" if os.getenv('STREAMLIT_PASSWORD') else None
    }
    st.write(env_vars)