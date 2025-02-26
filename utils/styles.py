def load_all_styles():
    """Carga todos los estilos CSS de la aplicación"""
    import streamlit as st
    
    st.markdown("""
        <style>
        /* Control inmediato de sidebar y navegación - Poner al inicio */
        [data-testid="stSidebar"][aria-expanded="false"],
        [data-testid="stSidebar"][aria-expanded="true"],
        div[data-testid="collapsedControl"],
        section[data-testid="stSidebarNav"],
        button[kind="menuButton"],
        .stDeployButton,
        div[class^="stToolbar"] {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            height: 0 !important;
            position: absolute !important;
            z-index: -1 !important;
            margin: 0 !important;
            padding: 0 !important;
        }        
        
        /* Importar fuente similar a Rockwell (Google Fonts no tiene Rockwell) */
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;700&display=swap');
        
        /* Aplicar fuente a toda la aplicación */
        * {
            font-family: 'Roboto Slab', serif !important;
        }
        
        /* Estilos principales */
        .main-title {
            text-align: left;
            font-size: 2.5em;
            margin-bottom: 0;
            color: #001F3F;
            font-weight: bold;
        }
        .subtitle {
            text-align: left;
            font-size: 1.8em;
            color: #001F3F;
            margin-top: 0;
            font-weight: bold;
        }
        
        /* Contenedor del autor */
        .author-container {
            position: fixed;
            right: 20px;
            bottom: 60px;
            text-align: right;
            color: #001F3F;
            font-weight: bold;
            z-index: 1000;
        }
        
        /* Contenedor del footer */
        .footer-container {
            position: fixed;
            bottom: 0;
            right: 0;
            padding: 10px;
            z-index: 1000;
        }
        .footer img {
            max-width: 200px;
        }
        
        /* Estilos de login */
        .login-box {
            max-width: 300px;
            margin: 0 auto;
            padding: 10px;
        }
        div[data-testid="stTextInput"] input {
            max-width: 200px !important;
            display: block;
        }
        div[data-testid="stTextInput"] {
            max-width: 280px !important;
            margin: 0 auto !important;
        }
        button[kind="primary"] {
            max-width: 120px !important;
            margin: 0 auto !important;
            display: block !important;
        }
        div[data-baseweb="notification"] {
            width: 100% !important;
            max-width: 300px !important;
            margin: 0 auto !important;
        }
        
        /* Estilos globales */
        .stTextInput input, .stTextInput label {
            color: #001F3F !important;
            font-size: 0.9em !important;
            max-width: 200px !important;
        }
        
        /* Color global de texto */
        .st-emotion-cache-*, div, p, h1, h2, h3, label {
            color: #001F3F !important;
        }        
        /* Ajustes responsivos mejorados */
        @media (max-width: 1200px) {
            .main-title { font-size: 2.2em; }
            .subtitle { font-size: 1.6em; }
        }
        @media (max-width: 768px) {
            .main-title { font-size: 1.8em; }
            .subtitle { font-size: 1.4em; }
            div[data-testid="stImage"] img { max-width: 150px !important; }
        }
        @media (max-width: 480px) {
            .main-title { font-size: 1.5em; }
            .subtitle { font-size: 1.2em; }
            div[data-testid="stImage"] img { max-width: 100px !important; }
        }
        </style>
    """, unsafe_allow_html=True)