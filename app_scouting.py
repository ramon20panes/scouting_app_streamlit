import streamlit as st
from common.session import init_session_state
from utils.auth import login, check_auth
from pathlib import Path

st.set_page_config(
    page_title="Atlético de Madrid 24/25",
    page_icon="⚽",
    layout="wide"
)

# Rutas de las imágenes
ESCUDO_PATH = Path("assets/escudos/atm.png")
FOOTER_PATH = Path("assets/logos/footer.png")

def main():
    init_session_state()
    
    # Estilos CSS personalizados
    st.markdown("""
        <style>
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
            max-width: 250px;
            margin: 0 auto;
            padding: 10px;
        }
        div[data-testid="stTextInput"] {
            width: 200px !important;
            margin: 0 auto;
        }
        div[data-testid="stButton"] {
            width: 200px !important;
            margin: 0 auto;
        }
        
        /* Estilos globales */
        .stTextInput input, .stTextInput label {
            color: #001F3F !important;
            font-size: 0.9em !important;
            max-width: 200px !important;
        }
        
        /* Sidebar capitalización */
            .st-emotion-cache-eczf16 span {
            text-transform: capitalize !important;
        }
        
        /* Color global de texto */
        .st-emotion-cache-*, div, p, h1, h2, h3, label {
            color: #001F3F !important;
        }
        
        /* Ajustes responsivos */
        @media (max-width: 768px) {
            .main-title { font-size: 2em; }
            .subtitle { font-size: 1.5em; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Estructura del contenido
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(str(ESCUDO_PATH), width=200)

    with col2:
        st.markdown('<h1 class="main-title">Club Atlético de Madrid</h1>', unsafe_allow_html=True)
        st.markdown('<h2 class="subtitle">Dirección Deportiva</h2>', unsafe_allow_html=True)

    # Autor
    st.markdown("""
        <div class="author-container">
            Ramón González<br>
            Mod8 MPAD
        </div>
    """, unsafe_allow_html=True)

    # Login
    if not check_auth():
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            login()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success('¡Bienvenido al panel de análisis!', icon="✅")
        st.switch_page("pages/1_Historico.py")
    
    # Footer
    st.markdown(f"""
        <div class="footer-container">
            <img src="data:image/png;base64,{base64_image(str(FOOTER_PATH))}" style="max-width: 200px;">
        </div>
    """, unsafe_allow_html=True)

def base64_image(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

if __name__ == "__main__":
    main()