import streamlit as st
from common.session import init_session_state
from utils.auth import login, check_auth
from pathlib import Path
import base64
from utils.styles import load_all_styles

# Configuración de la página
st.set_page_config(
    page_title="Atlético de Madrid 24/25",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar menú de hamburguesa y demás elementos
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# Cargar estilos al principio del archivo
load_all_styles()

# Rutas de las imágenes
ESCUDO_PATH = Path("assets/escudos/atm.png")
FOOTER_PATH = Path("assets/logos/footer.png")

def base64_image(image_path):
    """Convierte imagen a base64 para insertarla en HTML"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()  

# Ocultar la sidebar en la página principal
st.markdown("""
    <style>
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"],
    div[data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        position: absolute !important;
        z-index: -1 !important;
    }
    </style>
""", unsafe_allow_html=True)    
       
def main():
    # Inicializar estado de sesión
    init_session_state()
    
    # Cargar estilos CSS
    load_all_styles()
    
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
    # Código más específico y agresivo para ocultar la sidebar y el botón
    if not check_auth():
        st.markdown("""
            <style>
            /* Ocultar sidebar y sus elementos */
            [data-testid="stSidebar"] {
                display: none !important;
            }
            div[data-testid="collapsedControl"] {
                display: none !important;
            }
            .css-1d391kg {
                display: none !important;
            }
            section[data-testid="stSidebarNav"] {
                display: none !important;
            }
            /* Ocultar botón de recarga y otros controles */
            .stApp > header {
                display: none !important;
            }
            .stDeployButton {
                display: none !important;
            }
            </style>
        """, unsafe_allow_html=True)

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

