import streamlit as st

def init_session_state():
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False