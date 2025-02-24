import streamlit as st

def init_session_state():
    """Inicializa todas las variables de estado de la sesión"""
    
    # Estado de autenticación
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False
    
    # Variable para redirecciones
    if "redirect_to" not in st.session_state:
        st.session_state.redirect_to = None
    
    # Otras variables potencialmente útiles
    if "current_page" not in st.session_state:
        st.session_state.current_page = None
        
    if "selected_metrics" not in st.session_state:
        st.session_state.selected_metrics = []

    if "page_history" not in st.session_state:
        st.session_state.page_history = []

    