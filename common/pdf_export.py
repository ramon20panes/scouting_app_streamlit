import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

def export_to_pdf(data_dict, filename="informe_atletico.pdf", title="Informe Atlético de Madrid", figures=None):
    """
    Función principal para exportar datos a PDF.
    
    Args:
        data_dict (dict): Diccionario con secciones y datos a exportar
        filename (str): Nombre del archivo a descargar
        title (str): Título del informe
        figures (dict): Diccionario con nombres y objetos de figuras matplotlib
    
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
                # Agregar espacio antes de la tabla
                pdf.ln(2)
                
                # Inicializar col_widths con un valor predeterminado
                col_widths = []
                
                # Verificar que el DataFrame no esté vacío
                if not section_data.empty and len(section_data.columns) > 0:
                    # Obtener el número de columnas y calcular el ancho
                    col_count = len(section_data.columns)
                    
                    # Por defecto, dividir equitativamente, pero con ajustes para columnas de nombres
                    for col in section_data.columns:
                        if col.lower() in ['jugador', 'nombre', 'player']:
                            col_widths.append(60)  # Más espacio para nombres
                        else:
                            col_widths.append(25)  # Espacio estándar para métricas
                    
                    # Ajustar si la suma es mayor que el ancho disponible
                    available_width = 180  # Ancho disponible en mm
                    if sum(col_widths) > available_width:
                        scale = available_width / sum(col_widths)
                        col_widths = [w * scale for w in col_widths]
                    
                    # Encabezados con color de fondo
                    pdf.set_fill_color(232, 232, 232)  # Gris claro
                    pdf.set_font('Arial', 'B', 8)
                    
                    for i, header in enumerate(section_data.columns):
                        pdf.cell(col_widths[i], 7, str(header), 1, 0, 'C', True)
                    pdf.ln()
                    
                    # Configurar el formato para los datos
                    pdf.set_font('Arial', '', 8)
                    
                    # Alternar colores para las filas
                    for row_idx, (_, row) in enumerate(section_data.iterrows()):
                        # Alternar colores de fondo para mejor legibilidad
                        if row_idx % 2 == 0:
                            pdf.set_fill_color(255, 255, 255)  # Blanco
                        else:
                            pdf.set_fill_color(245, 245, 245)  # Gris muy claro
                        
                        for i, val in enumerate(row):
                            # Formatear valores numéricos con 2 decimales si son floats
                            if isinstance(val, float):
                                val_str = f"{val:.2f}"
                            else:
                                val_str = str(val)
                            
                            # Alineación: nombres a la izquierda, números al centro
                            align = 'L' if i == 0 and section_data.columns[i].lower() in ['jugador', 'nombre', 'player'] else 'C'
                            pdf.cell(col_widths[i], 6, val_str, 1, 0, align, True)
                        pdf.ln()
                else:
                    # Si el DataFrame está vacío, mostrar un mensaje
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 10, "No hay datos disponibles para esta sección", 0, 1, 'C')
                
                # Espacio después de la tabla
                pdf.ln(3)
            
            elif isinstance(section_data, str):
                # Texto simple
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 5, section_data)
            
            # Espacio entre secciones
            pdf.ln(5)
            
            # Si hay una figura asociada a esta sección, añadirla
            if figures and section_title in figures:
                # Guardar la figura en un archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
                    tmp_img_path = tmp_img.name
                
                fig = figures.get(section_title)
                fig.savefig(tmp_img_path, format='png', dpi=150, bbox_inches='tight')
                
                # Ajustar el tamaño para que quepa en la página
                img_width = 180  # Ancho máximo en mm (el ancho del papel es ~210mm)
                pdf.image(tmp_img_path, x=15, w=img_width)
                
                # Eliminar archivo temporal de imagen
                os.unlink(tmp_img_path)
                
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