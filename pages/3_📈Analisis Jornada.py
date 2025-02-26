import streamlit as st
import pandas as pd
import numpy as np
from utils.auth import check_auth, logout
from common.pdf_export import export_to_pdf, download_pdf_button
import base64
from datetime import datetime
from pathlib import Path
from utils.styles import load_all_styles

# Configuración de la página
st.set_page_config(
    page_title="Atlético de Madrid 24/25",
    page_icon="⚽",
    layout="wide"
)

# Cargar estilos al principio del archivo
load_all_styles()

# Mostrar la sidebar explícitamente
st.markdown("""
    <style>
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"],
    div[data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
        position: relative !important;
        z-index: 1 !important;
        margin: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Añadir reducción de márgenes y espaciados
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
}
div[data-testid="stVerticalBlock"] > div {
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if not check_auth():
    st.switch_page("Aplic_Direcc_Deport.py")

# Título centrado
ESCUDO_PATH = Path("assets/escudos/atm.png")

# Título con escudo (modificado para ser más compacto)
col_title, col_logo = st.columns([5, 1])

with col_title:
    st.write("")
    st.markdown("""
        <h2 style='text-align: left; margin-top: -15px; margin-bottom: -10px;'>
            Análisis Post_Partido
        </h2>
    """, unsafe_allow_html=True)

with col_logo:
    st.write("")  # Esto añade un pequeño espacio vertical
    st.image(ESCUDO_PATH, width=70)  # Reducir el tamaño del escudo

# Reducir el espacio antes de los tabs
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    margin-bottom: -25px;
}
div[data-testid="stTabs"] {
    margin-top: -20px;
}
div[data-testid="stTabContent"] {
    padding-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Obtener el nombre de la página actual
current_page = __file__.split('\\')[-1]

# Inicializar y actualizar el historial
if "page_history" not in st.session_state:
    st.session_state.page_history = []

# Actualizar historial solo si es una página nueva
if not st.session_state.page_history or st.session_state.page_history[-1] != current_page:
    st.session_state.page_history.append(current_page)

# Crear contenedor para botón de PDF y footer sin línea divisoria
st.markdown("---")
footer_container = st.container()

with footer_container:
   
    footer_cols = st.columns([1, 2, 1])
    
    # Columna izquierda - Botón PDF con texto incluido
    with footer_cols[0]:
        if st.button("📑 Exportar Informe PDF", key="generate_pdf"):
            pdf_data = {
                "Información General": "Visualizaciones Atlético de Madrid temporada 24/25",
                "Gráficos": "Resumen de visualizaciones generadas",
                # Añade los datos específicos de esta página
            }

            # Generar PDF
            pdf_bytes = export_to_pdf(
                pdf_data, 
                filename=f"informe_atm_{datetime.now().strftime('%d%m%Y')}.pdf",
                title="Informe Atlético de Madrid - Métricas 24/25"
            )
            
            # Mostrar botón de descarga - MOVIDO DENTRO DEL BLOQUE IF
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.pdf_filename = f"informe_atm_{datetime.now().strftime('%d%m%Y')}.pdf"
            st.success("PDF generado correctamente")

        # Si hay un PDF generado, mostrar el botón de descarga
        if "pdf_bytes" in st.session_state and st.session_state.pdf_bytes:
            download_pdf_button(
                st.session_state.pdf_bytes,
                filename=st.session_state.pdf_filename
            )
    
    # Columna central - Espacio vacío
    with footer_cols[1]:
        pass
    
    # Columna derecha - Solo autor, ajustado verticalmente
    with footer_cols[2]:
        st.markdown("""
            <div style="text-align: right; margin-top: 5px;">
                <strong>Ramón González</strong><br>
                Mod8 MPAD
            </div>
        """, unsafe_allow_html=True)

    # CSS adicional para que el footer se vea correctamente con el botón PDF
st.markdown("""
    <style>
    /* Ajustes para la sección del footer */
    .author-container {
        position: relative !important;
        text-align: right;
        margin-top: 20px;
    }
    .footer-container {
        position: relative !important;
        text-align: right;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    # Espacio flexible
    st.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)
    
    # Botones al final
    container = st.container()
    with container:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back"):
                if len(st.session_state.page_history) > 1:
                    # Quitar página actual
                    st.session_state.page_history.pop()
                    # Ir a página anterior
                    previous_page = st.session_state.page_history[-1]
                    st.switch_page(f"pages/{previous_page}")
        with col2:
            if st.button("Exit"):
                logout()

    # CSS para posicionar los botones
    st.markdown("""
        <style>
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:last-child {
            position: fixed;
            bottom: 20px;
            padding: 1rem;
            width: inherit;
        }
        </style>
    """, unsafe_allow_html=True)
    