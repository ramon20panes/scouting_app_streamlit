import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

class PDFWithLogo(FPDF):
    """FPDF personalizado con capacidad para incluir logo y otros elementos"""
    
    def header(self):
        # Logo
        try:
            self.image('assets/escudos/atm.png', 10, 8, 20)
            self.set_xy(35, 10)
        except Exception:
            self.set_xy(10, 10)
        
        # Título
        self.set_font('Arial', 'B', 20)
        self.set_text_color(0, 51, 153) 
        self.cell(0, 10, self.title, 0, 1, 'C')
        
        # Fecha
        self.set_font('Arial', 'B', 10)
        self.set_xy(self.w - 60, 10)
        self.set_text_color(0, 51, 153)  
        self.cell(50, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
                
        # Espacio después del encabezado
        self.ln(10)  # Reducido de 10 a 5 para optimizar espacio

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
        # Crear un PDF en orientación horizontal
        pdf = PDFWithLogo(orientation='L')
        pdf.title = title  
        pdf.alias_nb_pages()  
        
        # Colores del Atlético de Madrid
        rojo_atm = (210, 20, 43)  # Rojo Atlético
        azul_atm = (0, 51, 153)   # Azul Atlético
        
        # Márgenes más reducidos
        pdf.set_margins(5, 25, 5)  
        
        # Primera página
        pdf.add_page()
        
        # Agrupar figuras con sus títulos para procesarlas juntas
        grouped_content = []
        
        # Primera pasada: agrupar títulos con su contenido para evitar separaciones
        for section_title, section_data in data_dict.items():
            group = {"title": section_title, "data": section_data}
            if figures and section_title in figures:
                group["figure"] = figures[section_title]
            
            grouped_content.append(group)
        
        # Segunda pasada: procesar cada grupo (título + contenido) como una unidad
        for group in grouped_content:
            section_title = group["title"]
            section_data = group["data"]
            
            # Estimar altura total del grupo
            group_height = 15  # Altura base (título + espacios)
            
            # Estimar altura de datos
            if isinstance(section_data, pd.DataFrame) and not section_data.empty:
                rows = min(len(section_data), 20)  
                group_height += 6 + (rows * 5) + 5  
            elif isinstance(section_data, str):
                lines = len(section_data) / 80
                group_height += lines * 5
            
            # Estimar altura de figura
            has_figure = "figure" in group
            if has_figure:
                if "Mapa de tiros" in section_title:
                    group_height += 70  # Menor para mapas de tiros
                elif "Redes de pases" in section_title:
                    group_height += 150  # Mayor para redes de pases
                else:
                    group_height += 120  # Estándar para otras visualizaciones
            
            # REGLA ESTRICTA: Seguir título con visualización correspondiente
            important_visualization = has_figure and (
                "Mapa de tiros" in section_title or
                "Redes de pases" in section_title or
                "Expected Goals" in section_title
            )
            
            if pdf.get_y() + group_height > pdf.h - 30 or important_visualization:
                pdf.add_page()
            
            # 1. Título
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(azul_atm[0], azul_atm[1], azul_atm[2])
            pdf.cell(0, 6, section_title, 0, 1, 'L')
            pdf.ln(2)
            
            # 2. Datos
            pdf.set_text_color(0, 51, 153)
            
            if isinstance(section_data, pd.DataFrame) and not section_data.empty:
                # Anchos de columna
                col_count = len(section_data.columns)
                available_width = pdf.w - 10
                col_widths = []
                
                for col in section_data.columns:
                    if col.lower() in ['jugador', 'nombre', 'player', 'equipo', 'team']:
                        col_widths.append(40)  # Espacio para nombres
                    else:
                        col_widths.append((available_width - 40) / (col_count - 1))
                
                # Encabezados
                pdf.set_fill_color(rojo_atm[0], rojo_atm[1], rojo_atm[2])
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('Arial', 'B', 8)
                
                for i, header in enumerate(section_data.columns):
                    pdf.cell(col_widths[i], 6, str(header), 1, 0, 'C', True)
                pdf.ln()
                
                # Líneas y datos
                pdf.set_draw_color(azul_atm[0], azul_atm[1], azul_atm[2])
                pdf.set_text_color(0, 51, 153)
                pdf.set_font('Arial', 'B', 7)
                
                # Mostrar filas
                for row_idx, (_, row) in enumerate(section_data.iterrows()):
                    # Verificar si queda espacio en la página
                    if pdf.get_y() + 6 > pdf.h - 10:
                        pdf.add_page()
                        
                        # Repetir encabezados
                        pdf.set_fill_color(rojo_atm[0], rojo_atm[1], rojo_atm[2])
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font('Arial', 'B', 8)
                        
                        for i, header in enumerate(section_data.columns):
                            pdf.cell(col_widths[i], 6, str(header), 1, 0, 'C', True)
                        pdf.ln()
                        
                        pdf.set_text_color(0, 51, 153)
                        pdf.set_font('Arial', 'B', 7)
                    
                    # Alternar colores
                    if row_idx % 2 == 0:
                        pdf.set_fill_color(255, 255, 255)
                    else:
                        pdf.set_fill_color(240, 240, 240)
                    
                    # Dibujar fila
                    for i, val in enumerate(row):
                        if isinstance(val, float):
                            val_str = f"{val:.2f}"
                        else:
                            val_str = str(val)
                        
                        align = 'L' if i == 0 and section_data.columns[i].lower() in ['jugador', 'nombre', 'player', 'equipo', 'team'] else 'C'
                        pdf.cell(col_widths[i], 5, val_str, 1, 0, align, True)
                    pdf.ln()
            
            elif isinstance(section_data, str):
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(0, 5, section_data)
            
            pdf.ln(5)  # Espacio después de datos
            
            # 3. Dibujar figura si existe
            if has_figure:
                # Verificar nuevamente el espacio disponible
                if pdf.get_y() > pdf.h - 100:
                    pdf.add_page()
                    
                    # Repetir título solo si pasamos a nueva página
                    pdf.set_font('Arial', 'B', 11)
                    pdf.set_text_color(azul_atm[0], azul_atm[1], azul_atm[2])
                    pdf.cell(0, 6, f"{section_title} (continuación)", 0, 1, 'L')
                    pdf.ln(2)
                
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
                        tmp_img_path = tmp_img.name
                    
                    fig = group["figure"]
                    
                    # Tratamiento específico por tipo de visualización
                    if "Mapa de tiros" in section_title:
                        # Reducir más los mapas de tiros
                        fig.set_size_inches(4, 2.5)  # Muy pequeño
                        dpi_value = 72
                        img_width = 120
                    elif "Redes de pases" in section_title:
                        fig.set_size_inches(9, 6)
                        dpi_value = 100
                        img_width = 240
                    else:
                        fig.set_size_inches(8, 4.5)
                        dpi_value = 100
                        img_width = 200
                    
                    # Guardar figura
                    fig.savefig(tmp_img_path, format='png', dpi=dpi_value, bbox_inches='tight')
                    
                    # Insertar imagen centrada
                    pdf.image(tmp_img_path, x=(pdf.w - img_width)/2, w=img_width)
                    
                    os.unlink(tmp_img_path)
                    pdf.ln(5)
                except Exception as e:
                    pdf.set_text_color(255, 0, 0)
                    pdf.set_font('Arial', 'I', 8)
                    pdf.cell(0, 4, f"Error al procesar figura: {str(e)}", 0, 1, 'C')
                    pdf.set_text_color(0, 51, 153)
            
            # Espacio adicional entre grupos
            pdf.ln(6)
        
        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
        
        pdf.output(tmp_path)
        
        # Leer bytes
        with open(tmp_path, 'rb') as file:
            pdf_bytes = file.read()
        
        os.unlink(tmp_path)
        
        return pdf_bytes
    
    except Exception as e:
        st.error(f"Error al generar el PDF: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
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
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-button">📥 Descargar PDF</a>'
        
        st.markdown("""
        <style>
        .download-button {
            display: inline-block;
            padding: 8px 16px;
            background-color: #003399; /* Azul del Atleti */
            color: white !important;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 10px;
        }
        .download-button:hover {
            background-color: #002266; /* Azul más oscuro al pasar el ratón */
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(href, unsafe_allow_html=True)
        return True
    return False