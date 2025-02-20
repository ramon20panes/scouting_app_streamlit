import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

def check_auth():
    """Verifica si el usuario está autenticado"""
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False
    return st.session_state.authentication_status

def login():
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False
        
    if not st.session_state.authentication_status:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            username = st.text_input("Usuario", key="username")
            password = st.text_input("Contraseña", type="password", key="password")
            
            if st.button("Login", key="login_button", use_container_width=True):
                if username == "admin" and password == "admin":
                    st.session_state.authentication_status = True
                    placeholder = st.empty()
                    with placeholder.container():
                        st.success('¡Login exitoso!', icon="✅")
                    st.rerun()
                else:
                    st.error('Usuario o contraseña incorrectos', icon="🚨")