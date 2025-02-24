import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

def export_to_pdf(data_dict, filename="informe_atletico.pdf", title="Informe Atlético de Madrid"):
    """
    Función principal para exportar datos a PDF.
    
    Args:
        data_dict (dict): Diccionario con secciones y datos a exportar
        filename (str): Nombre del archivo a descargar
        title (str): Título del informe
    
    Returns:
        bytes: PDF en formato de bytes
    """
    try:
        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, title, 0, 1, 'C')
        
        # Fecha
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
        
        # Contenido
        for section_title, section_data in data_dict.items():
            # Título de sección
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, section_title, 0, 1, 'L')
            
            # Datos de la sección
            if isinstance(section_data, pd.DataFrame):
                # Convertir DataFrame a tabla
                pdf.set_font('Arial', 'B', 8)
                
                # Encabezados
                col_width = 180 / len(section_data.columns)
                for header in section_data.columns:
                    pdf.cell(col_width, 7, str(header), 1, 0, 'C')
                pdf.ln()
                
                # Datos
                pdf.set_font('Arial', '', 8)
                for _, row in section_data.iterrows():
                    for val in row:
                        pdf.cell(col_width, 6, str(val), 1, 0, 'C')
                    pdf.ln()
            
            elif isinstance(section_data, str):
                # Texto simple
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 5, section_data)
            
            # Espacio entre secciones
            pdf.ln(5)
        
        # Guardar en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
        
        pdf.output(tmp_path)
        
        # Leer archivo como bytes
        with open(tmp_path, 'rb') as file:
            pdf_bytes = file.read()
        
        # Eliminar archivo temporal
        os.unlink(tmp_path)
        
        return pdf_bytes
    
    except Exception as e:
        st.error(f"Error al generar el PDF: {str(e)}")
        return None

def download_pdf_button(pdf_data, filename="informe_atletico.pdf"):
    """
    Crea un botón para descargar el PDF generado.
    
    Args:
        pdf_data (bytes): Datos del PDF
        filename (str): Nombre del archivo a descargar
    """
    if pdf_data:
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        return True
    return False