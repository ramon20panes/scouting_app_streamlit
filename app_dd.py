import streamlit as st
from common.session import init_session_state
from utils.auth import login, check_auth
from pathlib import Path
import base64

# Configuración de la página
st.set_page_config(
    page_title="Atlético de Madrid 24/25",
    page_icon="⚽",
    layout="wide"
)

# Rutas de las imágenes
ESCUDO_PATH = Path("assets/escudos/atm.png")
FOOTER_PATH = Path("assets/logos/footer.png")

def base64_image(image_path):
    """Convierte imagen a base64 para insertarla en HTML"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def load_css():
    """Carga todos los estilos CSS de la aplicación"""
    st.markdown("""
        <style>
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
        
        /* Capitalización del sidebar */
        nav[data-testid="stSidebar"] ul li a p {
            text-transform: capitalize !important;
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

def main():
    # Inicializar estado de sesión
    init_session_state()
    
    # Cargar estilos CSS
    load_css()
    
    # Estructura del contenido
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(str(ESCUDO_PATH), width=200)

    with col2:
        st.markdown('<h1 class="main-title">Club Atlético de Madrid</h1>', unsafe_allow_html=True)
        st.markdown('<h2 class="subtitle">Dirección Deportiva</h2>', unsafe_allow_html=True)

    # Autor
    st.markdown(f"""
        <div class="author-container">
            Ramón González<br>
            Mod8 MPAD
        </div>
    """, unsafe_allow_html=True)

    # Login y navegación
    if not check_auth():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            login()  # Todo el manejo lo hace la función login
    else:
        # Ya autenticado, realizar redirección si es necesario
        if "redirect_to" in st.session_state and st.session_state.redirect_to:
            target_page = st.session_state.redirect_to
            st.session_state.redirect_to = None  # Limpiar
            st.switch_page(f"pages/{target_page}.py")
    
    # Footer
    st.markdown(f"""
        <div class="footer-container">
            <img src="data:image/png;base64,{base64_image(str(FOOTER_PATH))}" style="max-width: 200px;">
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()